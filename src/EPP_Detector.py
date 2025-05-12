import sys
import threading
from PyQt5.QtWidgets import (QApplication, QLabel, QVBoxLayout, QWidget, 
                             QPushButton, QFileDialog, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from ultralytics import YOLO
import cv2

class YOLOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitoreo EPP")
        self.setGeometry(100, 100, 800, 600)

        self.modelo_ruta = 'models/lastColab.pt'
        self.input_path = None
        self.modelo = YOLO(self.modelo_ruta)
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_video)
        self.video_thread = None

        self.init_ui()

    def init_ui(self):
        self.label_original = QLabel("Imagen original aparecerá aquí")
        self.label_original.setAlignment(Qt.AlignCenter)
        self.label_resultado = QLabel("Resultado aparecerá aquí")
        self.label_resultado.setAlignment(Qt.AlignCenter)

        self.btn_seleccionar = QPushButton("Seleccionar archivo")
        self.btn_seleccionar.clicked.connect(self.seleccionar_archivo)

        self.btn_procesar = QPushButton("Procesar")
        self.btn_procesar.clicked.connect(self.procesar)
        self.btn_procesar.setEnabled(False)

        self.btn_camara = QPushButton("Usar cámara")
        self.btn_camara.clicked.connect(self.iniciar_camara)

        self.btn_detener = QPushButton("Detener cámara")
        self.btn_detener.clicked.connect(self.detener_camara)
        self.btn_detener.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_seleccionar)
        btn_layout.addWidget(self.btn_procesar)
        btn_layout.addWidget(self.btn_camara)
        btn_layout.addWidget(self.btn_detener)

        layout = QVBoxLayout()
        layout.addWidget(self.label_original)
        layout.addWidget(self.label_resultado)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def seleccionar_archivo(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", 
            "Media Files (*.jpg *.jpeg *.png *.mp4 *.avi);;All Files (*)", 
            options=options)

        if file_path:
            self.input_path = file_path
            self.btn_procesar.setEnabled(True)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.mostrar_imagen_previa(file_path)
            else:
                self.label_original.setText("Video seleccionado")

    def mostrar_imagen_previa(self, path):
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.label_original.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))

    def procesar(self):
        if not self.input_path:
            return

        if self.cap:
            self.cap.release()
            self.timer.stop()

        if self.input_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.procesar_imagen()
        else:
            self.iniciar_video(self.input_path)

    def procesar_imagen(self):
        img = cv2.imread(self.input_path)
        resultados = self.modelo(img)[0]
        img = self.dibujar_cuadros_personalizados(img, resultados)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.label_resultado.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))

    def iniciar_video(self, path):
        self.cap = cv2.VideoCapture(path)
        if self.cap.isOpened():
            self.label_original.hide()
            self.timer.start(30)

    def iniciar_camara(self):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.label_original.hide()
            self.btn_detener.setEnabled(True)
            self.video_thread = threading.Thread(target=self.leer_camara)
            self.video_thread.start()

    def leer_camara(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            resultados = self.modelo(frame)[0]
            frame = self.dibujar_cuadros_personalizados(frame, resultados)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.label_resultado.setPixmap(pixmap.scaled(800, 500, Qt.KeepAspectRatio))

    def detener_camara(self):
        if self.cap:
            self.cap.release()
        self.label_resultado.clear()
        self.label_original.show()
        self.btn_detener.setEnabled(False)

    def actualizar_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            return
        resultados = self.modelo(frame)[0]
        frame = self.dibujar_cuadros_personalizados(frame, resultados)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.label_resultado.setPixmap(pixmap.scaled(800, 500, Qt.KeepAspectRatio))

    def dibujar_cuadros_personalizados(self, img, resultados):
        clases_detectadas = [int(cls) for cls in resultados.boxes.cls.tolist()]
        nombres_clases = [self.modelo.names[cls] for cls in clases_detectadas]

        epp_requerido = {'helmet', 'vest', 'gloves'}
        epp_detectado = set(nombres_clases)

        if epp_detectado >= epp_requerido:
            color = (0, 255, 0)  # Verde
        elif epp_detectado & epp_requerido:
            color = (0, 255, 255)  # Amarillo
        else:
            color = (0, 0, 255)  # Rojo

        for box, cls in zip(resultados.boxes.xyxy, resultados.boxes.cls):
            x1, y1, x2, y2 = map(int, box)
            label = self.modelo.names[int(cls)]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.9, color, 2)
        return img

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = YOLOApp()
    ventana.show()
    sys.exit(app.exec_())
