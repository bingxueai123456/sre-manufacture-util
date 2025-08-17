
import sys
import json
import qrcode
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit, QFileDialog,
    QSizePolicy, QSplitter
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Slot, QEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRE 制造工具")
        # 允许窗口自由缩放并设置合适的初始尺寸/最小尺寸
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

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
            QPushButton:pressed {
                background-color: rgba(0, 70, 145, 1.0);
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
            # Use QTextEdit for dynamic height
            widget = QTextEdit()
            self.inputs[name] = widget
            form_layout.addRow(label, widget)

        # Dropdown for serverType
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["", "NONE", "SRE_TCP"])
        self.inputs["serverType"] = self.server_type_combo
        form_layout.addRow("Server Type (SSL配置)", self.server_type_combo)
        
        # 使用容器包裹表单布局，便于设置主布局的伸缩策略
        form_container = QWidget()
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

        # --- Action Buttons ---
        generate_button = QPushButton("生成")
        generate_button.clicked.connect(self.generate_qr_code)
        main_layout.addWidget(generate_button)

        # --- Results Display (使用分割器以支持水平拉伸) ---
        # QR Code Image
        self.qr_image_label = QLabel("二维码将显示在这里")
        self.qr_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.qr_image_label.setMinimumSize(320, 320)
        # 监听二维码区域大小变化，动态重绘
        self.qr_image_label.installEventFilter(self)

        # JSON Content
        self.json_content_display = QTextEdit()
        self.json_content_display.setReadOnly(True)
        self.json_content_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.results_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.results_splitter.addWidget(self.qr_image_label)
        self.results_splitter.addWidget(self.json_content_display)
        # 避免任一子项被压缩为 0 宽度
        self.results_splitter.setChildrenCollapsible(False)
        # 使左侧二维码区域占比更大
        self.results_splitter.setStretchFactor(0, 3)
        self.results_splitter.setStretchFactor(1, 2)
        # 拖动分割条时同步更新二维码显示
        self.results_splitter.splitterMoved.connect(self._on_results_splitter_moved)
        main_layout.addWidget(self.results_splitter)
        
        # --- Bottom Buttons ---
        self.download_button = QPushButton("下载二维码")
        self.download_button.clicked.connect(self.download_qr_code)
        self.download_button.setEnabled(False) # Disabled until QR is generated
        main_layout.addWidget(self.download_button)

        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_all_fields)
        main_layout.addWidget(clear_button)

        self.qr_data = None # To hold the generated QImage
        self._splitter_initialized = False

        # 设置主布局的伸缩策略：结果区域更多占比以便在窗口变化时自适应
        # 索引：0=form_container, 1=generate_button, 2=results_splitter, 3=download_button, 4=clear_button
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 0)
        main_layout.setStretch(2, 1)
        main_layout.setStretch(3, 0)
        main_layout.setStretch(4, 0)

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

        # 根据当前显示区域尺寸自适应绘制
        self._update_qr_pixmap()
        
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
        # 窗口大小变化时自适应重绘二维码
        self._update_qr_pixmap()
        super().resizeEvent(event)

    def showEvent(self, event):
        # 首次显示时，设置结果分割区为 60% (左) / 40% (右)
        super().showEvent(event)
        if not self._splitter_initialized and hasattr(self, "results_splitter"):
            sizes = self.results_splitter.sizes()
            total = sum(sizes) if sizes else 0
            if total <= 0:
                # 给定一个合理的默认比例
                self.results_splitter.setSizes([3, 2])
            else:
                left = int(total * 0.6)
                right = max(1, total - left)
                self.results_splitter.setSizes([left, right])
            self._splitter_initialized = True

    def eventFilter(self, obj, event):
        # 监听二维码 QLabel 的尺寸变化
        if obj is self.qr_image_label and event.type() == QEvent.Resize:
            self._update_qr_pixmap()
        return super().eventFilter(obj, event)

    @Slot(int, int)
    def _on_results_splitter_moved(self, pos, index):
        # 分割条拖动后重绘二维码
        self._update_qr_pixmap()

    def _update_qr_pixmap(self):
        if not self.qr_data:
            return
        pixmap = QPixmap.fromImage(self.qr_data)
        self.qr_image_label.setPixmap(pixmap.scaled(
            self.qr_image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
