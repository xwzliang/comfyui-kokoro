import numpy as np
import torch
from kokoro_onnx import Kokoro
import logging
import os
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json"

MODEL_FILENAME = "kokoro-v0_19.onnx"
VOICES_FILENAME = "voices.json"

def download_file(url, file_name, path):
    if not os.path.exists(path):
        os.makedirs(path)
    with requests.get(url, stream=True, allow_redirects=True) as response:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 4096  # 4KB blocks
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name)
        with open(path+file_name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()


class KokoroSpeaker:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "speaker_name": (
                    [
                        "af",
                        "af_sarah",
                        "af_bella",
                        "af_nicole",
                        "af_sky",
                        "am_adam",
                        "am_michael",
                        "bf_emma",
                        "bf_isabella",
                        "bm_george",
                        "bm_lewis",
                    ],
                    {"default": "af_sarah"},
                ),
            },
        }

    RETURN_TYPES = ("KOKORO_SPEAKER",)
    RETURN_NAMES = ("speaker",)

    FUNCTION = "select"

    CATEGORY = "kokoro"

    def __init__(self):
        self.kokoro = None
        self.node_dir = os.path.dirname(os.path.abspath(__file__))
        self.voices_path = os.path.join(self.node_dir, VOICES_FILENAME)
        self.model_path = os.path.join(self.node_dir, MODEL_FILENAME)

    def select(self, speaker_name):
        if not os.path.exists(self.voices_path):
            download_file(VOICES_URL, VOICES_FILENAME, self.node_dir+"/")
            download_file(MODEL_URL, MODEL_FILENAME, self.node_dir+"/")
        kokoro = Kokoro(self.model_path, self.voices_path)
        speaker: np.ndarray = kokoro.get_voice_style(speaker_name)
        return ({"speaker": speaker},)

    @classmethod
    def IS_CHANGED(cls, speaker_name):
        return hash(speaker_name)

class KokoroSpeakerCombiner:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "speaker_a": ("KOKORO_SPEAKER", ),
                "speaker_b": ("KOKORO_SPEAKER", ),
                "weight": ("FLOAT", {"default": 0.5, "min": 0, "max": 1, "step": 0.05}),
            },
        }

    RETURN_TYPES = ("KOKORO_SPEAKER",)
    RETURN_NAMES = ("speaker",)

    FUNCTION = "combine"

    CATEGORY = "kokoro"

    def __init__(self):
        self.kokoro = None
        self.node_dir = os.path.dirname(os.path.abspath(__file__))
        self.voices_path = os.path.join(self.node_dir, VOICES_FILENAME)
        self.model_path = os.path.join(self.node_dir, MODEL_FILENAME)

    def combine(self, speaker_a, speaker_b, weight):

        if not os.path.exists(self.voices_path):
            download_file(VOICES_URL, VOICES_FILENAME, self.node_dir+"/")
            download_file(MODEL_URL, MODEL_FILENAME, self.node_dir+"/")
        weight = weight * 100.0
        weight_a = weight
        weight_b = 100.0 - weight
        speaker = np.add(speaker_a["speaker"] * (weight_a / 100.0), speaker_b["speaker"] * (weight_b / 100.0))

        return ({"speaker": speaker},)

    @classmethod
    def IS_CHANGED(cls, speaker_a, speaker_b, weight):
        return hash((speaker_a, speaker_b, weight))

class KokoroGenerator:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "I am a synthesized robot"}),
                "speaker": ("KOKORO_SPEAKER", ),
                "speed": ("FLOAT", {"default": 1, "min": 0.1, "max": 4, "step": 0.05}),
                "lang": ("STRING", {
                    "multiline": False,
                    "default": "en-us"
                }),

            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    FUNCTION = "generate"

    CATEGORY = "kokoro"

    def __init__(self):
        self.kokoro = None
        self.node_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.node_dir, MODEL_FILENAME)
        self.voices_path = os.path.join(self.node_dir, VOICES_FILENAME)

    def generate(self, text, speaker, speed, lang):

        if not os.path.exists(self.model_path) or not os.path.exists(self.voices_path):
            download_file(VOICES_URL, VOICES_FILENAME, self.node_dir+"/")
            download_file(MODEL_URL, MODEL_FILENAME, self.node_dir+"/")

        np_load_old = np.load
        np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)

        try:
            kokoro = Kokoro(model_path=self.model_path, voices_path=self.voices_path)
        except Exception as e:
             logger.error(f"ERROR: could not load kokoro-onnx in generate: {e}")
             np.load = np_load_old
             return (None,)

        try:
            audio, sample_rate = kokoro.create(text, voice=speaker["speaker"], speed=speed, lang=lang)
        except Exception as e:
            logger.error(f"{e}")
            np.load = np_load_old
            return (None,)

        if audio is None:
             logger.error("no audio is generated")
             np.load = np_load_old
             return (None,)

        np.load = np_load_old
        audio_tensor = torch.from_numpy(audio).unsqueeze(0).unsqueeze(0).float()  # Add a batch dimension AND a channel dimension

        return ({"waveform": audio_tensor, "sample_rate": sample_rate},) #return as tuple

    @classmethod
    def IS_CHANGED(cls, text, speaker, speed, lang):
        return hash((text, speaker, speed, lang))



NODE_CLASS_MAPPINGS = {
    "KokoroGenerator": KokoroGenerator,
    "KokoroSpeaker": KokoroSpeaker,
    "KokoroSpeakerCombiner": KokoroSpeakerCombiner,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KokoroGenerator": "Kokoro Generator",
    "KokoroSpeaker": "Kokoro Speaker",
    "KokoroSpeakerCombiner": "Kokoro Speaker Combiner",
}