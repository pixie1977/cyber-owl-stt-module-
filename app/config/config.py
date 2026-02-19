import os
from distutils.util import strtobool
from dotenv import load_dotenv


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

STT_USE_TORCH_MODEL_MANAGER_STR = os.getenv("STT_USE_TORCH_MODEL_MANAGER_STR")
if not STT_USE_TORCH_MODEL_MANAGER_STR:
    raise ValueError("Не задан STT_USE_TORCH_MODEL_MANAGER_STR в .env")

STT_USE_TORCH_MODEL_MANAGER_STR = strtobool(STT_USE_TORCH_MODEL_MANAGER_STR)

STT_SOUND_DEVICE_NAME = os.getenv("STT_SOUND_DEVICE_NAME")

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

STT_VOSK_MODEL_PATH = os.getenv("STT_VOSK_MODEL_PATH")
if not STT_VOSK_MODEL_PATH:
    STT_VOSK_MODEL_PATH = os.path.join(CURRENT_DIRECTORY, "..", "models", "vosk-model-small-ru-0.22")

STT_SPK_MODEL_PATH = os.getenv("STT_SPK_MODEL_PATH")
if not STT_SPK_MODEL_PATH:
    STT_SPK_MODEL_PATH = os.path.join(CURRENT_DIRECTORY, "..", "models", "vosk-model-spk-0.4")

STT_SAMPLE_VOICES_PATH = os.getenv("STT_SAMPLE_VOICES_PATH")
if not STT_SAMPLE_VOICES_PATH:
    STT_SAMPLE_VOICES_PATH = os.path.join(CURRENT_DIRECTORY,"../","resources", "sample_voices")

STT_DOC_ROOT = os.getenv("STT_DOC_ROOT")
if not STT_DOC_ROOT:
    STT_DOC_ROOT = os.path.join(CURRENT_DIRECTORY, "..", "content")

STT_PORT = os.getenv("STT_PORT")
if not STT_PORT:
    raise ValueError("Не задан STT_PORT в .env")
STT_PORT = int(STT_PORT)

STT_HOST = os.getenv("STT_HOST")
if not STT_HOST:
    raise ValueError("Не задан STT_HOST в .env")

STT_LOG_LEVEL = os.getenv("STT_LOG_LEVEL")
if not STT_LOG_LEVEL:
    raise ValueError("Не задан STT_LOG_LEVEL в .env")
