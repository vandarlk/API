from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. 数据库配置 (符合手册 SQL 数据库要求)
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 定义数据库模型
class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# 3. 定义数据传输模型 (Pydantic)
class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

    class Config:
        from_attributes = True

app = FastAPI(title="XJCO3011 Task API")

# 获取数据库连接的辅助函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 下面是满足 CRUD 要求的 4 个接口 ---

# 接口 1: 读取所有 (Read)
@app.get("/tasks", response_model=List[TaskSchema])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()

# 接口 2: 创建 (Create)
@app.post("/tasks", status_code=201)
def create_task(task: TaskSchema, db: Session = Depends(get_db)):
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# 接口 3: 更新 (Update)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskSchema, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = updated_task.title
    db_task.description = updated_task.description
    db_task.completed = updated_task.completed
    db.commit()
    return db_task

# 接口 4: 删除 (Delete)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Deleted successfully"}