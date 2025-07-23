from sqlalchemy.orm import Session
from . import models, schemas

def get_analysis(db: Session, analysis_id: int):
    return db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()

def create_analysis(db: Session, analysis: schemas.AnalysisCreate):
    db_analysis = models.Analysis(
        job_title=analysis.job_title,
        cv_filename=analysis.cv_filename,
        analysis_data=analysis.analysis_data
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis