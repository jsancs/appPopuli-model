import os
import base64

from modal import method
from .common import app, model_volume, MODEL_DIR
from .labels import PLAGAS


def resize_image(img_b64: str):
    import tensorflow as tf
    from io import BytesIO
    from PIL import Image
    from tensorflow.keras.preprocessing.image import img_to_array

    img_bytes = base64.b64decode(img_b64)
    img = Image.open(BytesIO(img_bytes))
    img = img.resize((224, 224))
    img = img_to_array(img)
    img = img.astype("float32") / 255.0

    return tf.expand_dims(img, axis=0)


@app.cls(
    gpu="T4",
    cpu=1.0,
    volumes={MODEL_DIR: model_volume},
)
class AppPopuliModel:
    @method()
    def generate(self, image: str):
        import tensorflow as tf

        if not hasattr(self, "_model"):
            model_volume.reload()
            self._model = tf.keras.models.load_model(f"{MODEL_DIR}/model/modelo.h5")

        input_data = resize_image(image)
        logits = self._model.predict(input_data)

        class_idx = tf.argmax(logits, axis=1).numpy()[0]
        class_name = PLAGAS[class_idx]
        confidence = float(logits[0][class_idx] * 100)

        return class_name, confidence


@app.local_entrypoint()
def main():
    image_path = os.path.join("example", "hoja-apr1.jpg")
    with open(image_path, "rb") as f:
        image_data = f.read()

    base64_image = base64.b64encode(image_data).decode("utf-8")

    import time

    model = AppPopuliModel()
    start_time = time.time()
    response = model.generate.remote(base64_image)
    elapsed_time = time.time() - start_time

    print(f"Prediction: {response[0]} ({response[1]:.2f}%)")
    print(f"Elapsed: {elapsed_time:.4f}s")
