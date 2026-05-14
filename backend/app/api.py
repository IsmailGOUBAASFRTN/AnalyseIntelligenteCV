from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
import json

from .services import file_parser, gemini_analyzer, report_generator
from .db import session, crud
from . import schemas

logger = logging.getLogger(__name__)

analysis_router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


def _validate_upload_file(file: UploadFile, label: str) -> bytes:
    """Lit, vérifie la taille et l'extension d'un fichier uploadé."""
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"{label} dépasse la taille maximale autorisée de 10 MB."
        )
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Type de fichier non supporté pour {label}. Formats acceptés : PDF, DOCX, TXT."
        )
    # Rembobiner pour que parse_file puisse re-lire
    import io
    file.file = io.BytesIO(content)
    return content


@analysis_router.post("/analyze", response_model=schemas.AnalysisResult)
def analyze_cvs(
    job_title: str = Form(None),
    job_description_file: UploadFile = File(None),
    cv_files: List[UploadFile] = File(...),
    db: Session = Depends(session.get_db)
):
    if not job_title and not job_description_file:
        raise HTTPException(status_code=400, detail="Un intitulé de poste ou une fiche de poste est requis.")

    if len(cv_files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 CV par analyse.")

    if job_description_file:
        _validate_upload_file(job_description_file, "La fiche de poste")
        job_description_text = file_parser.parse_file(job_description_file)
    else:
        job_description_text = f"Intitulé de poste : {job_title}"

    analysis_results = []
    for cv_file in cv_files:
        _validate_upload_file(cv_file, f"Le CV '{cv_file.filename}'")

        try:
            cv_text = file_parser.parse_file(cv_file)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        # Appel à l'API Gemini
        try:
            raw_analysis = gemini_analyzer.get_analysis(job_description_text, cv_text)
        except RuntimeError as e:
            logger.error("Erreur Gemini pour %s : %s", cv_file.filename, e)
            raise HTTPException(status_code=502, detail=str(e))

        try:
            analysis_data = json.loads(raw_analysis)
        except json.JSONDecodeError:
            logger.error("Réponse Gemini invalide (JSON) pour %s", cv_file.filename)
            raise HTTPException(status_code=500, detail="Erreur lors de l'analyse de la réponse de l'IA.")

        try:
            db_result = crud.create_analysis(
                db=db,
                analysis=schemas.AnalysisCreate(
                    job_title=job_title or job_description_file.filename,
                    cv_filename=cv_file.filename,
                    analysis_data=analysis_data
                )
            )
            analysis_results.append(db_result)
        except SQLAlchemyError as e:
            logger.error("Erreur BDD lors de la sauvegarde de %s : %s", cv_file.filename, e)
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde en base de données.")

    if not analysis_results:
        raise HTTPException(status_code=500, detail="Aucune analyse n'a pu être complétée.")

    return analysis_results[0]


@analysis_router.get("/export/{analysis_id}")
def export_analysis_pdf(analysis_id: int, db: Session = Depends(session.get_db)):
    if analysis_id <= 0:
        raise HTTPException(status_code=400, detail="Identifiant d'analyse invalide.")
    db_analysis = crud.get_analysis(db, analysis_id=analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")

    return report_generator.generate_pdf_report(db_analysis)