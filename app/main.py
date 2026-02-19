"""
Точка входа в приложение STT (Speech-to-Text).
Запускает сервер и фоновое прослушивание микрофона.
"""

import os
import uvicorn

from app.core.httpd import app, stt_engine, message_queue
from app.config.config import STT_HOST, STT_PORT, STT_LOG_LEVEL
from app.utils.stt_utils import start_listening


if __name__ == "__main__":
    """
    Запуск FastAPI-приложения с одновременным запуском фонового прослушивания.
    """
    start_listening(stt_engine, message_queue)

    uvicorn.run(
        app,
        host=STT_HOST,
        port=STT_PORT,
        log_level=STT_LOG_LEVEL,
    )