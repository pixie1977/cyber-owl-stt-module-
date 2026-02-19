# Флаг для управления фоновым потоком
import asyncio
import threading
from asyncio import Queue
from typing import Callable

from app.core.speech_to_text import Speech2Text

listening_active = False

def is_listening_active():
    return listening_active

# --- Функции работы с очередью ---
async def push_message(text: str, message_queue: Queue):
    """
    Добавляет сообщение в очередь распознанных фраз.
    """
    if text.strip():
        await message_queue.put(text.strip())
        global latest_transcript
        latest_transcript = text.strip()  # Обновляем последний текст


async def pop_all_messages(message_queue: Queue) -> str:
    """
    Вычитывает все накопленные сообщения из очереди и возвращает их одной строкой.
    Сообщения объединяются через пробел.
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


def run_stt_listener(stt_engine:Speech2Text, queue:Queue, callback:Callable):
    """
    Фоновая функция, запускающая прослушивание микрофона.
    Вызывает listen() из Speech2Text и отправляет распознанные фразы в очередь.
    """
    global listening_active
    listening_active = True
    print("🎙️ Запуск прослушивания микрофона...")

    try:
        # Метод listen должен быть генератором или вызывать callback
        for text in stt_engine.listen():
            if not listening_active:
                break
            asyncio.run(push_message(text, queue))
            if callable(callback):
              result=callback(text=text)
    except Exception as e:
        print(f"❌ Ошибка в фоновом потоке STT: {e}")
    finally:
        listening_active = False


def start_listening(stt_engine: Speech2Text, queue : Queue , on_result_callback=None)-> dict[str, str]:
    global listening_active
    if listening_active:
        return {"status": "already_running"}

    thread = threading.Thread(
        target=run_stt_listener,
        args=(stt_engine, queue, on_result_callback),
        daemon=True)
    thread.start()

    return {"status": "success"}


async def stop_listening():
    """
    Останавливает прослушивание микрофона.
    """
    global listening_active
    listening_active = False
    return {"status": "stopped"}

