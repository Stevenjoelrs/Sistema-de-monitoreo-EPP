# Sistema inteligente de monitoreo de Equipo de Protección Personal (EPP)

## Descripción

Este sistema usa modelos YOLO para identificar elementos de seguridad como cascos, chalecos, guantes y botas, mostrando los resultados de una interfaz grafica simple e intuitiva, además incluye una integracion con telegram para notificaciones.

# Requisitos
* Python 3.8 o superior
* SO: Windows/Linux/macOS
* Camara Web (para funcionamiento de deteccion en tiempo real)

# Dependencias

La lista de dependencias estan en `requirements.txt`.

# Instalación

Clonar el repositorio:

```
git clone https://github.com/Stevenjoelrs/Sistema-de-monitoreo-EPP.git
cd Sistema-de-monitoreo-EPP
```

Crear entorno virtual (recomendado):

```
python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\Scripts\activate     # Windows
```

Instalar dependencias:

```
pip install -r requirements.txt
```

Descargar los modelos YOLO y colocarlos en una carpeta `models/`:

* best.pt (modelo principal de EPP)
* bestBotas.pt (modelo para reconocer guantes y botas)

# Uso

Ejecuta la aplicación con:

```
python3 EPP_Detector.py
```

# Estructura del Código

Componentes principales:

1. Interfaz Gráfica(YOLOApp):
   * Barra superior con logos y titulo.
   * Area de visualizacion de imagenes/video/camara.
   * Controles inferiores(Selección, procesamiento y manejo de camara).
  
2. Logica de procesamiento:
   * modelo_epp: YOLO para cascos y chalecos.
   * modelo_guantes_botas: YOLO para guantes y botas.
   * Sistema de colores para indicar cumplimiento de EPP.
  
## Integracíon con Telegram:

   
## Metodos clave:
* `dibujar_cuadros_personalizados()`: Analiza detecciones y dibuja cuadros con colores segun cumplimiento.
* `iniciar_camara()`: Inicia el flujo de video desde cámara.
* `procesar_imagen()`: Maneja pipeline de detección en imagenes estaticas.

## Diseño de interfaz

* Tema: Azul corporativo(#0E2D54)
* Responsivo: Adapta tamaño de imagenes manteniendo relación de aspecto.
* Botones: estilo uniforme con feedback visual.

## Integración con Telegram

El sistema inicia un procesi paralelo para:

* Enviar notificaciones cuando se detecta falta de EPP.
* Configuracion en `telegram_bot/Main.py`

## Sistema de Alertas

Codigo de colores en las detecciones:

* Verde: Todos loos EPP requeridos detectados.
* Amarillo: Algunos EPP detectados.
* Rojo: Faltan EPP esenciales.

## Estructura de Directorios:

```
├── models/               # Modelos YOLO
├── src/
│   ├── assets/           # Recursos gráficos
│   └── telegram_bot/     # Código del bot
├── utils/                # Utilidades
├── main.py               # Aplicación principal
└── README.md             # Documentación
```

# Limitaciones:

* Requiere hardware con aceleración GPU para mejor rendimiento.
* Los modelos deben de estar calibrados para el entorno especifico
* La precision depende de la cantidad de horas entrenadas en los modelos YOLO. (Poco tiempo de entrenamiento: resultados variables).

