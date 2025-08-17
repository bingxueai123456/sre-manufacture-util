
import sys
import json
import qrcode
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit, QFileDialog,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Slot

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRE 制造工具")
        self.setGeometry(100, 100, 600, 750)

        # --- Global Styles for Buttons ---
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 123, 255, 0.9);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 86, 179, 0.95);
            }
            QPushButton:disabled {
                background-color: rgba(108, 117, 125, 0.7);
            }
        """)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Input Widgets ---
        self.inputs = {}
        form_layout = QFormLayout()
        
        # Define fields to be created
        # Format: (internal_name, display_label)
        text_fields = [
            ("sn", "SN (设备号)"),
            ("secret", "Secret (设备密钥)"),
            ("m", "M (主服务器地址)"),
            ("s", "S (备服务器地址)"),
            ("screenQr", "Screen QR (屏幕二维码内容)")
        ]

        for name, label in text_fields:
            # Use QTextEdit for dynamic height, but limit it
            widget = QTextEdit()
            widget.setMaximumHeight(80) # Allow expanding up to ~3-4 lines
            self.inputs[name] = widget
            form_layout.addRow(label, widget)

        # Dropdown for serverType
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["", "NONE", "SRE_TCP"])
        self.inputs["serverType"] = self.server_type_combo
        form_layout.addRow("Server Type (SSL配置)", self.server_type_combo)
        
        main_layout.addLayout(form_layout)

        # --- Action Buttons ---
        generate_button = QPushButton("生成")
        generate_button.clicked.connect(self.generate_qr_code)
        main_layout.addWidget(generate_button)

        # --- Results Display ---
        # QR Code Image
        self.qr_image_label = QLabel("二维码将显示在这里")
        self.qr_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.qr_image_label.setMinimumSize(250, 250)
        main_layout.addWidget(self.qr_image_label)

        # JSON Content
        self.json_content_display = QTextEdit()
        self.json_content_display.setReadOnly(True)
        self.json_content_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.json_content_display.setFixedHeight(150)
        main_layout.addWidget(self.json_content_display)
        
        # --- Bottom Buttons ---
        self.download_button = QPushButton("下载二维码")
        self.download_button.clicked.connect(self.download_qr_code)
        self.download_button.setEnabled(False) # Disabled until QR is generated
        main_layout.addWidget(self.download_button)

        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_all_fields)
        main_layout.addWidget(clear_button)

        self.qr_data = None # To hold the generated QImage

    @Slot()
    def generate_qr_code(self):
        data = {}
        device_host = {}

        # Collect data from input widgets
        for name, widget in self.inputs.items():
            value = ""
            if isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()

            if value: # Only add non-empty values
                if name in ["m", "s"]:
                    device_host[name] = value
                else:
                    data[name] = value
        
        if device_host:
            data["deviceHost"] = device_host

        if not data:
            self.qr_image_label.setText("没有有效输入以生成二维码")
            self.json_content_display.setText("")
            self.download_button.setEnabled(False)
            self.qr_data = None
            return

        # Generate JSON string
        json_string = json.dumps(data, indent=2, ensure_ascii=False)
        self.json_content_display.setText(json_string)

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QImage
        buffer = img.convert("RGBA").tobytes("raw", "RGBA")
        qimage = QImage(buffer, img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
        self.qr_data = qimage # Save for download

        # Display QImage in QLabel
        pixmap = QPixmap.fromImage(qimage)
        self.qr_image_label.setPixmap(pixmap.scaled(
            self.qr_image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        
        self.download_button.setEnabled(True)

    @Slot()
    def download_qr_code(self):
        if not self.qr_data:
            return

        sn_widget = self.inputs.get("sn")
        sn_value = sn_widget.toPlainText().strip() if sn_widget else ""
        default_filename = f"qr_{sn_value}.png" if sn_value else "qrcode.png"

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存二维码", 
            default_filename,
            "PNG Files (*.png);;All Files (*)"
        )

        if file_path:
            self.qr_data.save(file_path, "PNG")

    @Slot()
    def clear_all_fields(self):
        for widget in self.inputs.values():
            if isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        
        self.qr_image_label.setText("二维码将显示在这里")
        self.json_content_display.clear()
        self.download_button.setEnabled(False)
        self.qr_data = None

    def resizeEvent(self, event):
        # Re-scale pixmap on window resize
        if self.qr_data:
            pixmap = QPixmap.fromImage(self.qr_data)
            self.qr_image_label.setPixmap(pixmap.scaled(
                self.qr_image_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
