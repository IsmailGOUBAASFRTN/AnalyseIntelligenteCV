import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from . import models
from .. import schemas

logger = logging.getLogger(__name__)


def get_analysis(db: Session, analysis_id: int):
    if analysis_id <= 0:
        return None
    return db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()


def create_analysis(db: Session, analysis: schemas.AnalysisCreate):
    db_analysis = models.Analysis(
        job_title=analysis.job_title,
        cv_filename=analysis.cv_filename,
        analysis_data=analysis.analysis_data
    )
    db.add(db_analysis)
    try:
        db.commit()
        db.refresh(db_analysis)
    except IntegrityError as e:
        db.rollback()
        logger.error("Contrainte BD violée : %s", e)
        raise HTTPException(status_code=409, detail="Erreur d'intégrité en base de données.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Erreur BD lors de la création : %s", e)
        raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde en base de données.")
    return db_analysis