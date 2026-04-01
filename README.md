# AppPopuli+ AI model

En esta rama se encuentra la implementación de un microservicio en python para realizar las inferencias sobre las imágenes de la aplicación [AppPopuli](https://github.com/Psancs05/apppopuli).

### API

El microservicio está desarrollado con python y expone una API implementada con FastAPI que dispone de 2 endpoints:

- GET /api

  - Devuelve un mensaje de texto. Se puede utilizar para comprobar que la API está funcionando correctamente.

- POST /api
  - Genera la enfermedad o plaga predicha para una imágen haciendo inferencia con el modelo de IA.
  - Se tiene que mandar la imagen en formato base64 en el cuerpo de la petición.
  - Devuelve un texto con el nombre de la enfermedad o plaga detectada por el modelo.

### Dependecias

Para ejecutar esta aplicación se necesita únicamente el paquete de modal que se puede instalar con `pip install modal` o `pip install -r requirements.txt`.

### Despliegue

La aplicación se despliega utilizando el servicio de [Modal](https://modal.com/). Es una plataforma serverless para aplicaciones de IA, que ofrece máquinas preparadas con tarjetas gráficas para realizar inferencia con este tipo de modelos.

En este microservicio se utilizan 2 aplicaciones de modal, una para el modelo y la otra para la API.

Pasos para ejecutar el microservicio:

1.- Crear el volumen asociado con el modelo

```
modal volume create model-appPopuli
```

Suponiendo que tenemos el modelo en `./appPopuli_model/` (deberá estar en `./appPopuli_model/model/` y los archivos en esa carpeta)

```
modal volume put model-appPopuli appPopuli_model/
```

Podemos comprobar si se ha subido correctamente ejecutando

```
modal volume ls model-appPopuli model/
```

y viendo que se encuentren los archivos ahí. Queremos que el volumen tenga una carpeta `model/` con los archivos dentro.

2.- Desplegar la aplicación

```
modal deploy -m src.app
```

Desplegará tanto el modelo como la API en Modal.
Si queremos probar el modelo sin desplegar (solo ejecuta), podemos hacer:

```
modal run -m src.setup_apppopuli
```

esto ejecutará el main (el método que tiene el decorador `@app.local_entrypoint()`) en la máquina de modal.

Podemos probar también a ejecutar la API sin hacer despliegue con:

```
modal serve -m src.app
```

y levantará la aplicación para hacer pruebas (cuidado con el tiempo de espera de la aplicación, si tardamos demasiado puede acabar la ejecución, ver `scaledown_window` en la app)

Si se ejecuta todo de forma correcta se desplegará la app y nos dará la url que podemos utilizar en el servicio de IA del frontend.
