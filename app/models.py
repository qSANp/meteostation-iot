from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime
from pydantic import BaseModel
from .database import Base

# Ссылка для SQLAlchemy (БД)
class WeatherDataModel(Base):
    __tablename__ = "weather_measurements"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Схема Pydantic для валидации данных из MQTT и API
class WeatherSchema(BaseModel):
    temperature: float
    humidity: float
    pressure: float

    class Config:
        from_attributes = True
