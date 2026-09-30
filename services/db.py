# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# Update with your actual PostgreSQL username and password
DATABASE_URL = "postgresql+psycopg2://postgres:Mayank123@host.docker.internal:5432/p102_rag"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatLog(Base):
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    target_document = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Automatically create the table in PostgreSQL if it doesn't exist
Base.metadata.create_all(bind=engine)