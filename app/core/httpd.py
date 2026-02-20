#!/usr/bin/env python3
"""
HTTP-сервер на FastAPI для STT с поддержкой GET и POST.
"""
from __future__ import annotations

import asyncio
import os
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config.config import STT_DOC_ROOT, STT_VOSK_MODEL_PATH, STT_SOUND_DEVICE_INDEX
from app.core.speech_to_text import Speech2Text
from app.utils.stt_utils import is_listening_active, pop_all_messages


app = FastAPI(title="STT API Server")

# Подключаем статические файлы
print(f"STT_DOC_ROOT={STT_DOC_ROOT}")
app.mount("/static", StaticFiles(directory=STT_DOC_ROOT), name="static")

# Инициализация
stt_engine = Speech2Text(
    model_path=STT_VOSK_MODEL_PATH,
    samplerate=16000,
    sound_device_index=STT_SOUND_DEVICE_INDEX,
)

# Асинхронная очередь для хранения распознанных фраз
message_queue = asyncio.Queue()

# Глобальная переменная для хранения последнего распознанного текста
latest_transcript = ""


# Модель для POST-запросов
class TextRequest(BaseModel):
    text: str


@app.get("/")
async def read_root():
    """
    Возвращает главную страницу приложения.

    :return: HTML-файл или JSON-ответ
    """
    index_path = os.path.join(STT_DOC_ROOT, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Cyber Owl Speech2Text API"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Проверка работоспособности сервиса.

    :return: статус сервиса
    """
    status = "OK" if stt_engine.healthcheck() == "OK" and is_listening_active() else "NOT OK"
    return {"server_status": "ok", "service": status}


@app.get("/api/stt/latest")
async def get_latest_transcript() -> Dict[str, str]:
    """
    Возвращает все накопленные распознанные фразы одной строкой и очищает очередь.

    :return: JSON с ключом 'text'
    """
    full_text = await pop_all_messages(message_queue)
    return {"text": full_text}


@app.post("/api/stt/text")
async def post_text(request: TextRequest) -> Dict[str, str]:
    """
    Принимает текстовую строку и добавляет её в очередь распознанных фраз.
    Может использоваться для тестирования или симуляции распознавания.

    :param request: объект с полем `text`
    :return: подтверждение приёма
    """
    global latest_transcript
    text = request.text.strip()

    # Добавляем в очередь
    await message_queue.put(text)
    latest_transcript = text

    return {"status": "received", "text": text}