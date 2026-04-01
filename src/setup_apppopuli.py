from modal import method, Volume
from .common import app

import os
import base64

MODELS_VOLUME = "model-appPopuli"
MODEL_DIR_BASE = "/vol/base-models"

app.model_volume = Volume.from_name(MODELS_VOLUME)


# Método para preprocesar las imágenes al formato del modelo
def resizeImages(img_b64):
    import tensorflow as tf
    from io import BytesIO
    from PIL import Image
    from tensorflow.keras.preprocessing.image import img_to_array

    # Decodificar la imagen en base64 a un objeto Image de PIL
    img_bytes = base64.b64decode(img_b64)
    img = Image.open(BytesIO(img_bytes))

    # Redimensionar la imagen
    img = img.resize((224, 224))
    img = img_to_array(img)
    img = img.astype("float32") / 255.0

    return tf.expand_dims(img, axis=0)


# Clase que ejecuta el modelo en la máquina de modal con GPU
@app.cls(
    gpu="T4",
    cpu=1.0,
    volumes={
        MODEL_DIR_BASE: app.model_volume,
    },
)
class AppPopuliModel:
    def __enter__(self):
        # Cuando se llama a la máquina con el modelo se recarga el volumen con los ficheros del modelo
        app.model_volume.reload()

    def __init__(self):
        # Al instanciar el modelo lo cargamos en memoria
        import tensorflow as tf

        with tf.device("/gpu:0"):
            self.model = tf.keras.models.load_model(f"{MODEL_DIR_BASE}/model/modelo.h5")

        # Lista de plagas que detecta el modelo
        self.plagas = [
            "Archips xylosteana",
            "Cerura iberica",
            "Chrysomela populi",
            "Cossus cossus",
            "Crepidodera spp",
            "Cryptorhynchus lapathi",
            "Cytospora chrysosperma",
            "Dothichiza populea",
            "Gypsonoma aceriana",
            "Laothoe populi",
            "Lepidosaphes ulmi",
            "Leucoma salicis",
            "Lonsdalea quercina subsp populi",
            "Marssonina brunnea",
            "Melampsora spp",
            "Melanophila picta",
            "Paranthrene tabaniformis",
            "Pemphigus spp",
            "Phloemyzus passerinii",
            "Phratora laticolis",
            "SANO",
            "Saperda carcharias",
            "Saperda populnea",
            "Sesia apiformis",
            "Taphrina populnea (Taphrina aurea)",
            "Trypophloeus spp",
            "Venturia populina",
            "Xanthomonas populi",
        ]

    @method()
    def generate(self, image):
        # Método que hace la inferencia sobre una imagen
        import tensorflow as tf

        # Preprocesamiento de la img
        input_data = resizeImages(image)

        # Inferencia del modelo
        logits = self.model.predict(input_data)

        # Convertimos el output en la plaga correspondiente
        class_idx = tf.argmax(logits, axis=1).numpy()[0]
        class_name = self.plagas[class_idx]
        confidence = logits[0][class_idx] * 100

        return class_name, confidence


#! Este método solo se ejecuta al hacer `modal run setup_apppopuli` (para probar)
@app.local_entrypoint()
def main():
    model = AppPopuliModel()

    image_path = os.path.join("chopos", "Venturia.jpg")
    with open(image_path, "rb") as file:
        image_data = file.read()

    base64_image = base64.b64encode(image_data).decode("utf-8")
    print(len(base64_image))

    import time

    start_time = time.time()
    response = model.generate.remote(base64_image)
    elapsed_time = time.time() - start_time

    print(f"Respuesta del modelo: {response}")
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print()
