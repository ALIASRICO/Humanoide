# Explicación de `yolo_run.py`

El archivo `yolo_run.py` está diseñado para facilitar y automatizar el entrenamiento de modelos YOLO (You Only Look Once) utilizando la librería [Ultralytics YOLO](https://docs.ultralytics.com/). Su propósito principal es permitir a los usuarios entrenar diferentes variantes de modelos YOLO de manera sencilla, modificando solo algunos parámetros clave.

## Desglose del código

1. **Importaciones**
    ```python
    from ultralytics import YOLO
    import torch
    ```
    Se importan las librerías necesarias para trabajar con modelos YOLO y para verificar la disponibilidad de GPU con PyTorch.

2. **Verificación de GPU**
    ```python
    print(f"GPU disponible: {torch.cuda.is_available()}")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU'}")
    ```
    Se imprime si hay una GPU disponible y el nombre de la GPU detectada, lo cual es útil para asegurarse de que el entrenamiento se realizará de manera eficiente.

3. **Selección del modelo YOLO**
    ```python
    model = YOLO('') # Colocamos el modelo a entrenar (por ejemplo, 'yolov8n.pt' o 'yolov8s.pt')
    ```
    Aquí se debe especificar el modelo YOLO que se desea entrenar, como `'yolov8n.pt'` (nano), `'yolov8s.pt'` (small), etc. Esto permite experimentar fácilmente con diferentes arquitecturas.

4. **Entrenamiento del modelo**
    ```python
    results = model.train(
         data='', # Ruta del archivo .yaml con la configuración del dataset
         epochs=150,
         imgsz=640,
         batch=16,
         device=0,
         workers=8,
         patience=50,
         save=True,
         project='runs/train',
         name=''
    )
    ```
    - **data**: Ruta al archivo `.yaml` que describe el dataset personalizado.
    - **epochs**: Número de épocas de entrenamiento.
    - **imgsz**: Tamaño de las imágenes de entrada.
    - **batch**: Tamaño del batch (ajustable según la memoria de la GPU).
    - **device**: Selección de GPU.
    - **workers**: Número de procesos para cargar datos.
    - **patience**: Número de épocas sin mejora antes de detener el entrenamiento.
    - **save**: Guarda los checkpoints del modelo.
    - **project** y **name**: Organización de los resultados y experimentos.

## Propósito

Este script sirve como plantilla flexible para entrenar distintos modelos YOLO sobre diferentes datasets, simplemente cambiando los parámetros del modelo y la ruta de los datos. Así, facilita la experimentación y comparación entre modelos y configuraciones, acelerando el proceso de desarrollo en tareas de visión por computadora.
