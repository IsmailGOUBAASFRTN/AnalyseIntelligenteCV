from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from .services import file_parser, gemini_analyzer, report_generator
from .db import session, crud
from . import schemas

analysis_router = APIRouter()

@analysis_router.post("/analyze", response_model=schemas.AnalysisResult)
def analyze_cvs(
    job_title: str = Form(None),
    job_description_file: UploadFile = File(None),
    cv_files: List[UploadFile] = File(...),
    db: Session = Depends(session.get_db)
):
    if not job_title and not job_description_file:
        raise HTTPException(status_code=400, detail="Un intitulé de poste ou une fiche de poste est requis.")

    if job_description_file:
        job_description_text = file_parser.parse_file(job_description_file)
    else:
        job_description_text = f"Intitulé de poste : {job_title}"

    analysis_results = []
    for cv_file in cv_files:
        cv_text = file_parser.parse_file(cv_file)
        
        # Appel à l'API Gemini
        raw_analysis = gemini_analyzer.get_analysis(job_description_text, cv_text)
        
        try:
            analysis_data = json.loads(raw_analysis)
            # Sauvegarde en BDD
            db_result = crud.create_analysis(
                db=db, 
                analysis=schemas.AnalysisCreate(
                    job_title=job_title or job_description_file.filename,
                    cv_filename=cv_file.filename,
                    analysis_data=analysis_data
                )
            )
            analysis_results.append(db_result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Erreur lors de l'analyse de la réponse de l'IA.")
            
    # Pour simplifier, nous retournons le premier résultat pour la réponse API.
    # Une route /results/{id} serait plus appropriée pour une analyse multi-CV.
    if not analysis_results:
        raise HTTPException(status_code=500, detail="Aucune analyse n'a pu être complétée.")

    return analysis_results[0]

@analysis_router.get("/export/{analysis_id}")
def export_analysis_pdf(analysis_id: int, db: Session = Depends(session.get_db)):
    db_analysis = crud.get_analysis(db, analysis_id=analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    return report_generator.generate_pdf_report(db_analysis)