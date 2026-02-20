"""
Утилиты для работы с распознаванием речи: запуск прослушивания, управление очередью сообщений.
"""

from __future__ import annotations

import asyncio
import threading
from asyncio import Queue
from typing import Callable, Dict, Optional

from app.core.speech_to_text import Speech2Text


# Глобальные переменные
listening_active = False
latest_transcript = ""
main_loop: asyncio.AbstractEventLoop | None = None  # Будет установлен из основного потока


def is_listening_active() -> bool:
    """
    Проверяет, активно ли прослушивание микрофона.

    :return: True, если прослушивание активно.
    """
    return listening_active


async def push_message(text: str, message_queue: Queue) -> None:
    """
    Добавляет сообщение в очередь распознанных фраз и обновляет последний текст.

    :param text: распознанный текст.
    :param message_queue: асинхронная очередь для хранения сообщений.
    """
    if not text.strip():
        return
    await message_queue.put(text.strip())
    global latest_transcript
    latest_transcript = text.strip()


async def pop_all_messages(message_queue: Queue) -> str:
    """
    Вычитывает все накопленные сообщения из очереди и возвращает их одной строкой.

    :param message_queue: очередь сообщений.
    :return: объединённый текст всех сообщений через пробел.
    """
    messages = []
    try:
        while True:
            # Не ждём — если нет сообщений, выходим
            message = message_queue.get_nowait()
            messages.append(message)
    except asyncio.QueueEmpty:
        pass
    return " ".join(messages)


def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    """
    Устанавливает основной event loop для использования в фоновых потоках.

    :param loop: цикл событий из основного потока.
    """
    global main_loop
    main_loop = loop


def run_stt_listener(
    stt_engine: Speech2Text,
    queue: Queue,
    callback: Optional[Callable[[str], None]]
) -> None:
    """
    Фоновая функция, запускающая прослушивание микрофона.

    :param stt_engine: экземпляр движка распознавания речи.
    :param queue: очередь для добавления распознанных фраз.
    :param callback: опциональная функция обратного вызова при распознавании.
    """
    global listening_active, main_loop
    listening_active = True
    print("🎙️ Запуск прослушивания микрофона...")

    # Убедимся, что в потоке есть event loop (необходимо для Windows/uvicorn)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        for text in stt_engine.listen():
            if not listening_active:
                break
            if main_loop is not None:
                asyncio.run_coroutine_threadsafe(push_message(text, queue), main_loop)
            else:
                print(f"⚠️ Event loop не установлен. Сообщение пропущено: {text}")
            if callback is not None and callable(callback):
                callback(text)
    except Exception as e:
        print(f"❌ Ошибка в фоновом потоке STT: {e}")
    finally:
        listening_active = False


def start_listening(
    stt_engine: Speech2Text,
    queue: Queue,
    on_result_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, str]:
    """
    Запускает фоновое прослушивание микрофона в отдельном потоке.

    :param stt_engine: движок распознавания речи.
    :param queue: очередь для сохранения текста.
    :param on_result_callback: опциональный callback на каждое распознанное сообщение.
    :return: статус операции.
    """
    global listening_active
    if listening_active:
        return {"status": "already_running"}

    thread = threading.Thread(
        target=run_stt_listener,
        args=(stt_engine, queue, on_result_callback),
        daemon=True,
    )
    thread.start()

    return {"status": "success"}


async def stop_listening() -> Dict[str, str]:
    """
    Останавливает прослушивание микрофона.

    :return: статус операции.
    """
    global listening_active
    listening_active = False
    return {"status": "stopped"}