# Comfy UI Kokoro

Kokoro TTS nodes, based on this [kokoro repo](https://github.com/thewh1teagle/kokoro-onnx)

![workflow.png](.meta/workflow.png)

**note**: This picture is also a workflow, just download and drop it into comfy.

## Install

Clone the repo into `custom_nodes` folder, and reboot Comfy.

```shell
git clone https://github.com/stavsap/comfyui-kokoro.git
```

The model and speakers meta-data will be automatically downloaded on the first run.

## Nodes

Currently, there are 3 nodes that can be combined for TTS workflow.

### Kokoro Speaker

![speaker.png](.meta/speaker.png)

Select supported speakers.

### Kokoro Speaker Combiner

![speaker_combiner.png](.meta/speaker_combiner.png)

Combiner node to combine 2 given speakers to new speaker.

- **weight**: [1, 0], select the weight of `speaker a`.

Example:

`weight == 0.7` will result in strength of 70% of `speaker_a` and 30% of `speaker_b`.


### Kokoro Generate

![generator.png](.meta/generator.png)

- **speaker**: input a speaker
- **speed**: set the speach speed.
- **lang**: set the language, what ever is supported by kokoro.


## Available Voices

The following voices are available:
- **af** (African Female)
- **af_sarah** (African Female Sarah)
- **af_bella** (African Female Bella)
- **af_nicole** (African Female Nicole)
- **af_sky** (African Female Sky)
- **am_adam** (African Male Adam)
- **am_michael** (African Male Michael)
- **bf_emma** (British Female Emma)
- **bf_isabella** (British Female Isabella)
- **bm_george** (British Male George)
- **bm_lewis** (British Male Lewis)

## Use Cases:

1. TTS: Text To Speach, generate voice from test.

2. Lip Sync: sync lips of videos

![lipsync.png](.meta/lipsync.png)

## License

- [This repo](LICENSE)
- kokoro-onnx: MIT
- kokoro model: Apache 2.0

## Credits

- Kokoro TTS Engine: [Include credits for the original Kokoro TTS project]
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- [ComfyUI-BS_Kokoro-onnx](https://github.com/Burgstall-labs/ComfyUI-BS_Kokoro-onnx)
- [ComfyUI-KokoroTTS](https://github.com/benjiyaya/ComfyUI-KokoroTTS)
