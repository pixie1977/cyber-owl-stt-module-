import os

from app.core.httpd import app, stt_engine, message_queue
from app.config.config import STT_HOST, STT_PORT, STT_LOG_LEVEL
from app.utils.stt_utils import start_listening

if __name__ == "__main__":
    import uvicorn

    start_listening(stt_engine, message_queue)

    uvicorn.run(
        app,
        host=STT_HOST,
        port=STT_PORT,
        log_level=STT_LOG_LEVEL,
    )