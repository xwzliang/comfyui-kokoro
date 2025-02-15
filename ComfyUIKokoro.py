import numpy as np
import torch
#from kokoro_onnx import Kokoro
import logging
import os
import requests
from tqdm import tqdm
import io
#from misaki import en, espeak
#from misaki.zh import ZHG2P
import soundfile as sf
from kokoro import KPipeline

logger = logging.getLogger(__name__)

# MODEL_URL = "https://github.com/taylorchu/kokoro-onnx/releases/download/v0.2.0/kokoro.onnx"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
# MODEL_FILENAME = "kokoro_v1.onnx"
# VOICES_FILENAME = "voices_v1.bin"
MODEL_FILENAME = "kokoro-v1.0.onnx"
VOICES_FILENAME = "voices-v1.0.bin"

supported_languages_display = ["English", "English (British)","French", "Japanese", "Korean", "Mandarin Chinese", "Spanish"]

supported_languages = {
    supported_languages_display[0]: "en-us",
    supported_languages_display[1]: "en-gb",
    supported_languages_display[2]: "fr-fr",
    supported_languages_display[3]: "ja",
    supported_languages_display[4]: "ko",
    supported_languages_display[5]: "cmn",
    supported_languages_display[6]: "es",
}

supported_voices =[
    # American Female
    "af_heart",
    "af_alloy",
    "af_aoede",
    "af_bella",
    "af_jessica",
    "af_kore",
    "af_nicole",
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    #American Male
    "am_adam",
    "am_echo",
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa",
    # British Female
    "bf_alice",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    # British Male
    "bm_daniel",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    # Japanese Female
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    # Japanese Male
    "jm_kumo",

    "zf_xiaobei",
    "zf_xiaoni",
    "zf_xiaoxiao",
    "zf_xiaoyi",
    "zm_yunjian",
    "zm_yunxi",
    "zm_yunxia",
    "zm_yunyang",
    "ef_dora",
    "em_alex",
    "em_santa",
    "ff_siwis",
    "hf_alpha",
    "hf_beta",
    "hm_omega",
    "hm_psi",
    "if_sara",
    "im_nicola",
    "pf_dora",
    "pm_alex",
    "pm_santa",
]

def download_file(url, file_name, path):
    if not os.path.exists(path):
        os.makedirs(path)
    with requests.get(url, stream=True, allow_redirects=True) as response:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 4096  # 4KB blocks
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name)
        with open(os.path.join(path, file_name), 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()

def download_voices(path):
    file_path = os.path.join(path, VOICES_FILENAME)

    if os.path.exists(file_path):
        return
    
    download_file(VOICE_URL, VOICES_FILENAME, path)

    # names = supported_voices

    # pattern = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/{name}.pt"
    # voices = {}

    # for name in names:
    #     url = pattern.format(name=name)
    #     print(f"Downloading {url}")
    #     r = requests.get(url)
    #     r.raise_for_status()  # Ensure the request was successful
    #     content = io.BytesIO(r.content)
    #     data: np.ndarray = torch.load(content, weights_only=True).numpy()
    #     voices[name] = data

    # with open(file_path, "wb") as f:
    #     np.savez(f, **voices)
    # print(f"Created {file_path}")

def download_model(path):
    if os.path.exists(os.path.join(path, MODEL_FILENAME)):
        return
    download_file(MODEL_URL, MODEL_FILENAME, path)

class KokoroSpeaker:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "speaker_name": (
                    supported_voices,
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
    #    download_model(self.node_dir)
    #    download_voices(self.node_dir)
    #    kokoro = Kokoro(self.model_path, self.voices_path)
    #    speaker: np.ndarray = kokoro.get_voice_style(speaker_name)
    #    return ({"speaker": speaker},)
        return ({"speaker": speaker_name},)

    @classmethod
    def IS_CHANGED(cls, speaker_name):
        return hash(speaker_name)

class KokoroGenerator:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "I am a synthesized robot"}),
                "speaker": ("KOKORO_SPEAKER", ),
                "speed": ("FLOAT", {"default": 1, "min": 0.1, "max": 4, "step": 0.05}),
                "lang": (
                    supported_languages_display,
                    {"default": "English"
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
        #download_model(self.node_dir)
        #download_voices(self.node_dir)

        # np_load_old = np.load
        # np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)

        lang = supported_languages[lang]

        if lang is None:
            lang = "en-us"

        #try:
        #    kokoro = Kokoro(model_path=self.model_path, voices_path=self.voices_path)
        #except Exception as e:
        #     logger.error(f"ERROR: could not load kokoro-onnx in generate: {e}")
             # np.load = np_load_old
        #     return (None,)

        try:
            if lang == "cmn":
                # g2p = ZHG2P()
                # phonemes = g2p(text)
                # print(phonemes)
                # audio, sample_rate = kokoro.create(phonemes, voice=speaker["speaker"], speed=speed, lang=lang, is_phonemes=True, trim=False)
                pipeline = KPipeline(lang_code='z')
                generator = pipeline(
                    text, voice=speaker["speaker"], # <= change voice here
                    speed=speed, split_pattern=r'\n+'
                )
                for i, (gs, ps, audio_seg) in enumerate(generator):
                    print(i)  # i => index
                    print(gs) # gs => graphemes/text
                    print(ps) # ps => phonemes
                    # display(Audio(data=audio_seg, rate=24000, autoplay=i==0))
                    #sf.write(f'output/{i}.wav', audio_seg, 24000) # save each audio file
                    print(audio_seg)
                    audio, sample_rate = audio_seg, 24000
#            else:
                # Misaki G2P with espeak-ng fallback
#                fallback = espeak.EspeakFallback(british=False)
#                g2p = en.G2P(trf=False, british=False, fallback=fallback)
#                phonemes, _ = g2p(text)
#                audio, sample_rate = kokoro.create(phonemes, voice=speaker["speaker"], speed=speed, lang=lang, is_phonemes=True)
        except Exception as e:
            logger.error(f"{e}")
            # np.load = np_load_old
            return (None,)

        if audio is None:
             logger.error("no audio is generated")
             # np.load = np_load_old
             return (None,)

        # np.load = np_load_old
        #audio_tensor = torch.from_numpy(audio).unsqueeze(0).unsqueeze(0).float()  # Add a batch dimension AND a channel dimension
        audio_tensor = audio_seg.unsqueeze(0).unsqueeze(0).float()

        return ({"waveform": audio_tensor, "sample_rate": sample_rate},) #return as tuple

    @classmethod
    def IS_CHANGED(cls, text, speaker, speed, lang):
        return hash((text, speaker, speed, lang))



NODE_CLASS_MAPPINGS = {
    "KokoroGenerator": KokoroGenerator,
    "KokoroSpeaker": KokoroSpeaker,
#    "KokoroSpeakerCombiner": KokoroSpeakerCombiner,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KokoroGenerator": "Kokoro Generator",
    "KokoroSpeaker": "Kokoro Speaker",
#    "KokoroSpeakerCombiner": "Kokoro Speaker Combiner",
}
