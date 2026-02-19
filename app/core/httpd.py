#!/usr/bin/env python3
"""
HTTP-сервер на FastAPI для TTS с поддержкой POST, GET
"""
import asyncio
import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config.config import STT_DOC_ROOT, STT_VOSK_MODEL_PATH

# Импорт TTS движка
from app.core.speech_to_text import Speech2Text
from app.utils.stt_utils import is_listening_active, pop_all_messages

app = FastAPI(title="STT API Server")

# Подключаем статические файлы
print(f"STT_DOC_ROOT={STT_DOC_ROOT}")
app.mount("/static", StaticFiles(directory=STT_DOC_ROOT), name="static")

# Инициализация
stt_engine = Speech2Text(model_path=STT_VOSK_MODEL_PATH, samplerate=16000)

message_queue = asyncio.Queue()

# Глобальная переменная для хранения последнего распознанного текста
latest_transcript = ""


# Модель для JSON-запроса
class TTSTextRequest(BaseModel):
    text: str


@app.get("/")
async def read_root():
    index_path = os.path.join(STT_DOC_ROOT, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Cyber Owl Speech2Text API"}


@app.get("/health")
async def health_check():
    if stt_engine.healthcheck() == "OK" and is_listening_active():
        health_check_status = "OK"
    else:
        health_check_status = "NOT OK"
    return {"status": "ok", "service": health_check_status}


# Эндпоинт для получения последнего распознанного текста
@app.get("/api/stt/latest")
async def get_latest_transcript():
    """
    Возвращает последний распознанный фрагмент речи.
    """
    return {"text": await pop_all_messages(message_queue)}


