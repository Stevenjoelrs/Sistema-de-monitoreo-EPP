from ultralytics import YOLO
import os
import cv2

modelo_ruta = 'models/bestCollab.pt'
imagen_ruta = 'images/prueba8.jpeg'
directorio_salida = 'resultados'

os.makedirs(directorio_salida, exist_ok=True)

modelo = YOLO(modelo_ruta)

resultados = modelo(imagen_ruta)

for i, resultado in enumerate(resultados):
    img = resultado.plot(labels=False, conf=False)
    
    salida = os.path.join(directorio_salida, f"{os.path.basename(imagen_ruta)}")
    cv2.imwrite(salida, img)

print(f"Imagen guardada en: {salida}")


