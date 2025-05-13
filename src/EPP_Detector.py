import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QHBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from ultralytics import YOLO
from telegram_bot.Main import iniciar_bot
from telegram_bot.utils.Notifier import notify_group
from multiprocessing import Process
from utils.Run_Async_Task import run_async_task
import cv2


class YOLOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitoreo EPP")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)

        self.modelo_epp = YOLO('models/best.pt') 
        self.modelo_guantes_botas = YOLO('models/bestBotas.pt')
        self.input_path = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_video)
        self.video_thread = None

        self.init_ui()

    def init_ui(self):
        self.left_logo = QLabel()
        self.center_title = QLabel("SISTEMA DE DETECCIÓN DE EPP")
        self.right_logo = QLabel()

        self.left_logo.setPixmap(QPixmap("src/assets/pictures/logo.png").scaled(80, 80, Qt.KeepAspectRatio))
        self.right_logo.setPixmap(QPixmap("src/assets/pictures/umss.png").scaled(80, 80, Qt.KeepAspectRatio))
        self.center_title.setAlignment(Qt.AlignCenter)
        self.center_title.setStyleSheet("color: #DCE3EC; font-size: 24px; font-weight: bold;")

        top_hbox = QHBoxLayout()
        top_hbox.addWidget(self.left_logo, alignment=Qt.AlignLeft)
        top_hbox.addStretch(1)
        top_hbox.addWidget(self.center_title, alignment=Qt.AlignCenter)
        top_hbox.addStretch(1)
        top_hbox.addWidget(self.right_logo, alignment=Qt.AlignRight)

        self.label_original = QLabel("Imagen original aparecerá aquí")
        self.label_original.setAlignment(Qt.AlignCenter)
        self.label_original.setStyleSheet("color: white;")
        self.label_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.label_resultado = QLabel("Resultado aparecerá aquí")
        self.label_resultado.setAlignment(Qt.AlignCenter)
        self.label_resultado.setStyleSheet("color: white;")
        self.label_resultado.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.label_original)
        self.content_layout.addWidget(self.label_resultado)

        self.content_widget = QWidget()
        self.content_widget.setLayout(self.content_layout)

        self.btn_seleccionar = QPushButton("Seleccionar archivo")
        self.btn_seleccionar.clicked.connect(self.seleccionar_archivo)
        self.btn_procesar = QPushButton("Procesar")
        self.btn_procesar.clicked.connect(self.procesar)
        self.btn_procesar.setEnabled(False)
        self.btn_camara_iniciar = QPushButton("Usar cámara")
        self.btn_camara_iniciar.clicked.connect(self.iniciar_camara)
        self.btn_camara_detener = QPushButton("Detener cámara")
        self.btn_camara_detener.clicked.connect(self.detener_camara)
        self.btn_camara_detener.setEnabled(False)

        for btn in [self.btn_seleccionar, self.btn_procesar, self.btn_camara_iniciar, self.btn_camara_detener]:
            btn.setStyleSheet("background-color: #74A3C5; color: #0E2D54; font-weight: bold;")

        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(self.btn_seleccionar)
        bottom_hbox.addWidget(self.btn_procesar)
        bottom_hbox.addWidget(self.btn_camara_iniciar)
        bottom_hbox.addWidget(self.btn_camara_detener)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_hbox)
        main_layout.addWidget(self.content_widget, stretch=1)
        main_layout.addLayout(bottom_hbox)

        self.setStyleSheet("background-color: #0E2D54;")
        self.setLayout(main_layout)

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
        self.label_original.setPixmap(pixmap.scaled(
            self.label_original.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def procesar(self):
        if not self.input_path:
            return

        if self.cap:
            self.cap.release()
            self.timer.stop()
            self.label_original.show()

        if self.input_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.procesar_imagen()
        else:
            self.iniciar_video(self.input_path)

    def procesar_imagen(self):
        img = cv2.imread(self.input_path)
        resultados_epp = self.modelo_epp(img)[0]
        resultados_guantes_botas = self.modelo_guantes_botas(img)[0]
        img = self.dibujar_cuadros_personalizados(img, resultados_epp, resultados_guantes_botas)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.label_resultado.setPixmap(pixmap.scaled(
            self.label_resultado.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

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
            self.btn_camara_detener.setEnabled(True)
            self.video_thread = threading.Thread(target=self.leer_camara)
            self.video_thread.start()

    def leer_camara(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            resultados_epp = self.modelo_epp(frame)[0]
            resultados_guantes_botas = self.modelo_guantes_botas(frame)[0]
            frame = self.dibujar_cuadros_personalizados(frame, resultados_epp, resultados_guantes_botas)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.label_resultado.setPixmap(pixmap.scaled(
                self.label_resultado.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def detener_camara(self):
        if self.cap:
            self.cap.release()
        self.label_resultado.clear()
        self.label_original.show()
        self.btn_camara_detener.setEnabled(False)

    def actualizar_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            return
        resultados_epp = self.modelo_epp(frame)[0]
        resultados_guantes_botas = self.modelo_guantes_botas(frame)[0]
        frame = self.dibujar_cuadros_personalizados(frame, resultados_epp, resultados_guantes_botas)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.label_resultado.setPixmap(pixmap.scaled(
            self.label_resultado.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def dibujar_cuadros_personalizados(self, img, resultados_epp, resultados_guantes_botas):
        clases_no_deseadas = {'NO-Mask', 'Safety Cone', 'Vehicle'}
        epp_requerido = {'Hardhat', 'Safety Vest', '0'}
        epp_detectado = set()
        for box, cls in zip(resultados_epp.boxes.xyxy, resultados_epp.boxes.cls):
            x1, y1, x2, y2 = map(int, box)
            label = self.modelo_epp.names[int(cls)]
            if label not in clases_no_deseadas:
                epp_detectado.add(label)

        for box, cls in zip(resultados_guantes_botas.boxes.xyxy, resultados_guantes_botas.boxes.cls):
            x1, y1, x2, y2 = map(int, box)
            label = self.modelo_guantes_botas.names[int(cls)]
            epp_detectado.add(label)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        if epp_detectado >= epp_requerido:
            color_epp = (0, 255, 0)
        elif epp_detectado & epp_requerido:
            color_epp = (0, 255, 255)
        else:
            color_epp = (0, 0, 255)

        for box, cls in zip(resultados_epp.boxes.xyxy, resultados_epp.boxes.cls):
            x1, y1, x2, y2 = map(int, box)
            label = self.modelo_epp.names[int(cls)]
            if label not in clases_no_deseadas:
                cv2.rectangle(img, (x1, y1), (x2, y2), color_epp, 2)
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_epp, 2)
        return img

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        if self.timer.isActive():
            self.timer.stop()
        event.accept()


if __name__ == "__main__":
    bot_process = Process(target=iniciar_bot)
    bot_process.start()
    
    app = QApplication(sys.argv)
    ventana = YOLOApp()
    ventana.show()
    sys.exit(app.exec_())
    
    bot_process.terminate()
    sys.exit(exit_code)
