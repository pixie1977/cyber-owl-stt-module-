"""
Клиент для взаимодействия с STT-сервером.
Отправляет запросы на распознавание и получает результаты.
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any


class PostClient:
    """
    Асинхронный post-клиент для работы с API.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Инициализация клиента.

        :param base_url: URL STT-сервера.
        """
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "PostClient":
        """
        Контекстный менеджер: открывает сессию.
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Контекстный менеджер: закрывает сессию.
        """
        if self.session:
            await self.session.close()

    async def send_text(self, text: str) -> bool:
        """
        Отправляет текстовую строку на сервер через POST-запрос.

        :param text: текст для отправки.
        :return: True, если запрос успешен.
        """
        try:
            async with self.session.post(
                f"{self.base_url}/api/stt/text",
                json={"text": text}
            ) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"❌ Ошибка при отправке текста: {e}")
            return False

    async def poll_transcripts(self, interval: float = 2.0):
        """
        Периодически опрашивает сервер и возвращает новые распознанные фразы.

        :param interval: интервал опроса в секундах.
        :yields: распознанный текст (не пустой).
        """
        while True:
            transcript = await self.get_latest_transcript()
            if transcript:
                yield transcript
            await asyncio.sleep(interval)


# Пример использования
async def main():
    """
    Пример асинхронного использования клиента.
    """
    async with STTClient("http://127.0.0.1:8000") as client:
        if not await client.healthcheck():
            print("❌ Сервер STT недоступен")
            return

        print("✅ Подключено к STT-серверу. Отправка сообщения.")

        # Пример отправки текста
        await client.send_text("Это тестовое сообщение от клиента.")

        async for text in client.poll_transcripts(interval=1.5):
            print(f"📝 Ответ: {text}")


if __name__ == "__main__":
    asyncio.run(main())