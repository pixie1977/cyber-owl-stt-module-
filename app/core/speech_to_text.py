"""
Модуль для распознавания речи с использованием Vosk и sounddevice.
"""

import logging
import json
import queue
import sys
import os
from time import sleep
from typing import Generator

import sounddevice as sd
import vosk

from app.core.logger import get_logger


class Speech2Text:
    """
    Класс для потокового распознавания речи с микрофона.
    """

    _log = get_logger(__name__)
    _healthcheck = "OK"

    def __init__(
        self,
        model_path: str = "model",
        samplerate: int = 16000,
        sound_device_index: int = 0,
    ) -> None:
        """
        Инициализация движка распознавания речи.

        :param model_path: путь к модели Vosk
        :param samplerate: частота дискретизации аудио
        :param sound_device_index: индекс аудиоустройства
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Модель не найдена по пути: {model_path}")

        self._model = vosk.Model(model_path)
        self._rec = vosk.KaldiRecognizer(self._model, samplerate)
        self._q = queue.Queue()
        self._samplerate = samplerate
        self._sound_device_index = sound_device_index
        self._is_active = True

    def q_clear(self) -> None:
        """Очищает внутреннюю очередь аудиоданных."""
        with self._q.mutex:
            self._q.queue.clear()

    def q_callback(self, indata, frames, time, status) -> None:
        """
        Аудио-коллбэк: вызывается при поступлении новых данных с микрофона.

        :param indata: входной аудиобуфер
        :param frames: количество сэмплов
        :param time: временные метки
        :param status: статус потока (предупреждения/ошибки)
        """
        if status:
            self._log.warning(status)
        self._q.put(bytes(indata))

    def pause(self) -> None:
        """Приостанавливает прослушивание."""
        self._is_active = False

    def continue_listen(self) -> None:
        """
        Пропускает накопленные данные и возобновляет прослушивание.
        """
        result = json.loads(self._rec.Result())
        self._log.info("Пропущено: %s", result.get("text", ""))
        self.q_clear()
        self._is_active = True

    def listen(self) -> Generator[str, None, None]:
        """
        Генератор: возвращает распознанные фразы по мере их появления.

        :yields: текстовые строки
        """
        while self._is_active:
            try:
                with sd.RawInputStream(
                    samplerate=self._samplerate,
                    blocksize=16000,
                    device=self._sound_device_index,
                    dtype="int16",
                    channels=1,
                    callback=self.q_callback,
                ):
                    while self._is_active:
                        data = self._q.get()
                        if self._rec.AcceptWaveform(data):
                            text = json.loads(self._rec.Result())["text"]
                            if text.strip():
                                self._log.info(f"STT module detected text: {text}")
                                yield text
            except Exception as e:
                self._log.exception("Ошибка в процессе распознавания: %s", e)
                self._healthcheck = "BAD"
                sleep(1)

    def close(self) -> None:
        """Останавливает прослушивание и освобождает ресурсы."""
        self._is_active = False
        self._healthcheck = "BAD"
        self._log.info("STT module CLOSED")

    def healthcheck(self) -> str:
        """
        Возвращает состояние сервиса.

        :return: "OK" или "BAD"
        """
        return self._healthcheck