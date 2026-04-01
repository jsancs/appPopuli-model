from modal import App, Image, Volume

MODELS_VOLUME = "model-appPopuli"
MODEL_DIR = "/vol/base-models"

image = (
    Image.debian_slim(python_version="3.10")
    .pip_install("tensorflow==2.13.0")
    .pip_install("Pillow==10.4.0")
    .pip_install("Keras-Preprocessing")
    .pip_install("protobuf==3.20")
)

app = App(name="appPopuliModel", image=image)
model_volume = Volume.from_name(MODELS_VOLUME, create_if_missing=False)
