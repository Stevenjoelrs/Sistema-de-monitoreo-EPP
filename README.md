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
python3 main.py
```

