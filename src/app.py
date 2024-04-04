from modal import asgi_app
from .setup_apppopuli import AppPopuliModel
from .common import stub


@stub.function(
    container_idle_timeout=300,
    timeout=600,
)
@asgi_app()
def web():
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware

    # Config del servidor
    web_app = FastAPI()
    # Config de CORS
    origins = [
        "https://test.apppopuli.es",
    ]

    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Modelo para predicciones
    model = AppPopuliModel()

    @web_app.get("/")
    def ping():
        return {"estado": "ok", "resultado": "pong"}

    @web_app.post("/api")
    async def api(request: Request):
        try:
            # Leer la imagen del body
            data = await request.json()
            image_base64 = data.get("image")

            # Si no se pasa imagen se devuelve un error
            if image_base64 is None:
                raise HTTPException(
                    status_code=400, detail="No se proporcionó una imagen"
                )

            # Se predice la clase de la imagen y se devuelve el nombre de la plaga detectada
            output = model.generate.remote(image_base64)
            return {"estado": "ok", "resultado": output}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en el engine: {str(e)}")

    return web_app
