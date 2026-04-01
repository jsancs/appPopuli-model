from modal import App, Image


image = (
    Image.debian_slim(python_version="3.10")
    .pip_install("pillow")
    .pip_install("tensorflow==2.13.0")
    .pip_install("Keras-Preprocessing")
    .pip_install("protobuf==3.20")
)

app = App(name="appPopuliModel", image=image)
