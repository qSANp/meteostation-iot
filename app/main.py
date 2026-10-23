import json
import asyncio
import os
from gmqtt import Client as MQTTClient

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal, get_db
from .models import WeatherDataModel, WeatherSchema

# Создаем таблицы в БД при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weather IoT API")

# Конфигурация MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "weather/sensors")

# Настраиваем чтение шаблонов из папки
templates = Jinja2Templates(directory="app/templates")

def save_to_db(validated_data):
    db = SessionLocal()
    try:
        db_record = WeatherDataModel(
            temperature=validated_data.temperature,
            humidity=validated_data.humidity,
            pressure=validated_data.pressure
        )
        db.add(db_record)
        db.commit()
        print(f"[Database] Успешно сохранено: T={validated_data.temperature}, H={validated_data.humidity}, P={validated_data.pressure}")
    except Exception as db_err:
        print(f"[Database Error] Ошибка записи: {db_err}")
    finally:
        db.close()

# Коллбек при получении сообщения из MQTT
async def on_message(client, topic, payload, qos, properties):
    print(f"📥 [MQTT RAW] Получено сообщение в топик '{topic}': {payload.decode()}")

    try:
        data = json.loads(payload.decode())
        validated_data = WeatherSchema(**data)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, save_to_db, validated_data)
    except Exception as e:
        print(f"[MQTT Error] Ошибка обработки JSON: {e}")


# Фоновое подключение к MQTT при старте FastAPI
@app.on_event("startup")
async def start_mqtt():
    client = MQTTClient("fastapi_iot_client")
    client.on_message = on_message

    # 1. Вызываем подключение
    await client.connect(MQTT_BROKER, MQTT_PORT)

    # 2. Подписка
    client.subscribe(MQTT_TOPIC)

    print(f"[MQTT] Успешно подключились и подписались на топик: {MQTT_TOPIC}")


# Эндпоинт для главной страницы
@app.get("/", response_class=HTMLResponse)
def read_dashboard():
    # Напрямую открываем и читаем HTML-файл
    with open("app/templates/dashboard.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# Эндпоинт для истории
@app.get("/weather", response_model=list[WeatherSchema])
def get_weather_history(limit: int = 100, db: Session = Depends(get_db)):
    # Возвращение последних N записей из базы данных для графиков
    return db.query(WeatherDataModel).order_by(WeatherDataModel.id.desc()).limit(limit).all()
