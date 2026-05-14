from fastapi import UploadFile
import docx
import pypdf
import io
import logging

logger = logging.getLogger(__name__)

ALLOWED_MIME_SIGNATURES = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "docx",  # DOCX is a ZIP archive
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _detect_type(header: bytes, filename: str) -> str:
    """Détecte le vrai type du fichier via sa signature magique."""
    for sig, ftype in ALLOWED_MIME_SIGNATURES.items():
        if header.startswith(sig):
            return ftype
    # Fallback par extension pour les fichiers texte
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "txt":
        return "txt"
    return "unknown"


def parse_file(file: UploadFile) -> str:
    content = ""
    file_content = file.file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(f"Le fichier '{file.filename}' dépasse la taille maximale de 10 MB.")

    if len(file_content) == 0:
        raise ValueError(f"Le fichier '{file.filename}' est vide.")

    detected = _detect_type(file_content[:8], file.filename)

    if detected == "pdf":
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages[:50]:  # Max 50 pages
                text = page.extract_text()
                if text:
                    content += text + "\n"
        except Exception as e:
            logger.error("Erreur lors de la lecture du PDF '%s' : %s", file.filename, e)
            raise ValueError(f"Impossible de lire le PDF '{file.filename}' : fichier corrompu ou invalide.") from e

    elif detected == "docx":
        try:
            doc = docx.Document(io.BytesIO(file_content))
            for para in doc.paragraphs:
                content += para.text + "\n"
        except Exception as e:
            logger.error("Erreur lors de la lecture du DOCX '%s' : %s", file.filename, e)
            raise ValueError(f"Impossible de lire le fichier Word '{file.filename}' : fichier corrompu ou invalide.") from e

    elif detected == "txt":
        try:
            content = file_content.decode("utf-8", errors="ignore")
        except Exception as e:
            raise ValueError(f"Impossible de décoder le fichier texte '{file.filename}'.") from e

    else:
        raise ValueError(
            f"Type de fichier non supporté pour '{file.filename}'. "
            "Formats acceptés : PDF, DOCX, TXT."
        )

    # Nettoyage : normaliser les espaces et retirer les lignes vides consécutives
    lines = [line.strip() for line in content.split("\n")]
    content = "\n".join(line for line in lines if line)

    if not content:
        raise ValueError(f"Aucun texte n'a pu être extrait du fichier '{file.filename}'.")

    return content