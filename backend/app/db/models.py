from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    cv_filename = Column(String(255), nullable=False)
    analysis_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)