from modal import asgi_app
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .setup_apppopuli import AppPopuliModel
from .common import app


class PredictRequest(BaseModel):
    image: str


origins = [
    "https://test.apppopuli.es",
    "https://apppopuli.es",
]


@app.function(scaledown_window=300, timeout=600)
@asgi_app()
def web():
    web_app = FastAPI(title="AppPopuli Model API")

    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    model = AppPopuliModel()

    @web_app.get("/")
    def ping():
        return {"estado": "ok", "resultado": "pong"}

    @web_app.post("/api")
    async def api(request: Request):
        try:
            data = await request.json()
            image_base64 = data.get("image")

            if image_base64 is None:
                raise HTTPException(
                    status_code=400, detail="No se proporcionó una imagen"
                )

            class_name, confidence = model.generate.remote(image_base64)
            return {
                "estado": "ok",
                "resultado": f"{class_name} ({confidence:.2f}%)",
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en el engine: {str(e)}")

    return web_app
