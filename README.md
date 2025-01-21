# Comfy UI Kokoro

Kokoro TTS nodes, based on this [kokoro repo](https://github.com/thewh1teagle/kokoro-onnx)

![workflow.png](.meta/workflow.png)

note: this picture is also workflow, just drop it into comfy.

## Install

Clone the repo into `custom_nodes` folder, and reboot Comfy.

```shell
git clone https://github.com/stavsap/comfyui-kokoro.git
```

The model and speakers meta datat will be automatically downloads on the first run.

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