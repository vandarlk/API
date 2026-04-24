from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./medical_records.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Medical Record Model
class RecordModel(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    diagnosis = Column(String)
    treatment = Column(String)
    priority = Column(String, default="Normal") # Urgent, Normal, Routine
    is_discharged = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# 3. Pydantic Schemas
class RecordSchema(BaseModel):
    id: Optional[int] = None
    patient_name: str
    diagnosis: str
    treatment: str
    priority: str = "Normal"
    is_discharged: bool = False

    class Config:
        from_attributes = True

app = FastAPI(title="Healthcare EHR System API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints (CRUD + Filter) ---

# 1. Read with Filter (迭代功能：支持按紧急程度筛选)
@app.get("/records", response_model=List[RecordSchema])
def read_records(priority: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RecordModel)
    if priority:
        query = query.filter(RecordModel.priority == priority)
    return query.all()

# 2. Create
@app.post("/records", status_code=201)
def create_record(record: RecordSchema, db: Session = Depends(get_db)):
    db_record = RecordModel(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 3. Update
@app.put("/records/{record_id}")
def update_record(record_id: int, updated_record: RecordSchema, db: Session = Depends(get_db)):
    db_record = db.query(RecordModel).filter(RecordModel.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Patient record not found")
    for key, value in updated_record.dict().items():
        setattr(db_record, key, value)
    db.commit()
    return db_record

# 4. Delete
@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    db_record = db.query(RecordModel).filter(RecordModel.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(db_record)
    db.commit()
    return {"message": "Record deleted"}