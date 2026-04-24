 Features
Full CRUD Support: Create, Read, Update, and Delete tasks.

Data Persistence: Uses SQLAlchemy ORM with a SQLite database to ensure data is saved after server restarts.

Automated Documentation: Interactive API documentation powered by Swagger UI.

Robust Validation: Input data validation using Pydantic schemas.

 Tech Stack
Framework: FastAPI

Database: SQLite

ORM: SQLAlchemy

Language: Python 3.x

 Installation & Setup
git clone [https://github.com/vandarlk/API.git]
cd API

pip install fastapi[all] sqlalchemy

uvicorn main:app --reload

Access the API:

The API will be running at: http://127.0.0.1:8000

Interactive Documentation: Visit http://127.0.0.1:8000/docs to test the endpoints.