from . import graphviz, settings

from binaryninja import AnyFunctionType, Function
from binaryninjaui import getMonospaceFont  # pyright: ignore

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
)

from PySide6.QtCore import QDir, QFile, QIODevice, QTimer
from PySide6.QtGui import QPixmap

import subprocess


class ExportDialog(QDialog):
    function: Function

    styleDropdown: QComboBox
    fontDropdown: QComboBox
    fontSizeSpinner: QSpinBox

    contentSplitter: QSplitter
    codeArea: QPlainTextEdit
    previewImage: QLabel
    previewArea: QScrollArea

    copyDotButton: QPushButton
    copyPngButton: QPushButton
    cancelButton: QPushButton
    exportButton: QPushButton

    rootLayout: QVBoxLayout
    optionsLayout: QGridLayout
    buttonLayout: QHBoxLayout

    refreshTimer: QTimer

    def __init__(self, function: Function):
        super().__init__()

        self.function = function

        self.styleDropdown = QComboBox()
        self.styleDropdown.addItem("Disassembly")
        self.styleDropdown.addItem("LLIL")
        self.styleDropdown.addItem("MLIL")
        self.styleDropdown.addItem("HLIL")

        self.fontDropdown = QComboBox()
        self.fontDropdown.setEditable(True)
        self.fontDropdown.addItem(settings.default_font())

        self.fontSizeSpinner = QSpinBox()
        self.fontSizeSpinner.setMinimum(8)
        self.fontSizeSpinner.setMaximum(40)
        self.fontSizeSpinner.setValue(settings.default_font_size())

        self.codeArea = QPlainTextEdit()
        self.codeArea.setReadOnly(True)
        self.codeArea.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.codeArea.setFont(getMonospaceFont(self))

        self.previewImage = QLabel()
        self.previewImage.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.previewImage.setScaledContents(True)

        self.previewArea = QScrollArea()
        self.previewArea.setWidget(self.previewImage)

        self.contentSplitter = QSplitter()
        self.contentSplitter.addWidget(self.codeArea)
        self.contentSplitter.addWidget(self.previewArea)
        self.contentSplitter.setSizes([1, 1])

        self.copyDotButton = QPushButton("Copy DOT")
        self.copyPngButton = QPushButton("Copy PNG")
        self.cancelButton = QPushButton("Cancel")
        self.exportButton = QPushButton("Export...")
        self.exportButton.setDefault(True)

        self.optionsLayout = QGridLayout()
        self.optionsLayout.addWidget(QLabel("Style"), 0, 0)
        self.optionsLayout.addWidget(self.styleDropdown, 1, 0)
        self.optionsLayout.addWidget(QLabel("Font"), 0, 1)
        self.optionsLayout.addWidget(self.fontDropdown, 1, 1)
        self.optionsLayout.addWidget(QLabel("Size"), 0, 2)
        self.optionsLayout.addWidget(self.fontSizeSpinner, 1, 2)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.copyDotButton)
        self.buttonLayout.addWidget(self.copyPngButton)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.exportButton)

        self.rootLayout = QVBoxLayout()
        self.rootLayout.addLayout(self.optionsLayout)
        self.rootLayout.addWidget(self.contentSplitter, 1)
        self.rootLayout.addLayout(self.buttonLayout)

        self.refreshTimer = QTimer()
        self.refreshTimer.setSingleShot(True)

        self.styleDropdown.currentIndexChanged.connect(self.queueRefresh)
        self.fontDropdown.currentTextChanged.connect(self.queueRefresh)
        self.fontSizeSpinner.valueChanged.connect(self.queueRefresh)
        self.copyDotButton.clicked.connect(self.copyDot)
        self.copyPngButton.clicked.connect(self.copyPng)
        self.cancelButton.clicked.connect(self.reject)
        self.exportButton.clicked.connect(self.accept)
        self.refreshTimer.timeout.connect(self.refresh)

        self.setWindowTitle("Graphviz Export")
        self.setLayout(self.rootLayout)
        self.setMinimumSize(1024, 768)

        self.queueRefresh()

    def selectedFunction(self) -> AnyFunctionType:
        styleName = self.styleDropdown.currentText()
        if styleName == "LLIL":
            return self.function.llil
        elif styleName == "MLIL":
            return self.function.mlil
        elif styleName == "HLIL":
            return self.function.hlil
        else:
            return self.function

    def selectedFontName(self) -> str:
        return self.fontDropdown.currentText()

    def selectedFontSize(self) -> int:
        return self.fontSizeSpinner.value()

    def render(self, code: str) -> QPixmap:
        dotPath = QDir.temp().absoluteFilePath("bn_graphviz.dot")
        pngPath = QDir.temp().absoluteFilePath("bn_graphviz.png")

        with open(dotPath, "w") as dotFile:
            dotFile.write(code)

        subprocess.run(
            [
                settings.dot_executable_path(),
                "-Tpng",
                "-Gdpi=" + str(settings.raster_dpi()),
                "-o",
                pngPath,
                dotPath,
            ]
        )

        return QPixmap(pngPath)

    def queueRefresh(self):
        self.codeArea.setPlainText("Loading...")
        self.previewImage.setPixmap(QPixmap())
        self.refreshTimer.start(150)

    def refresh(self):
        dot = graphviz.to_dot(
            self.selectedFunction(),
            self.selectedFontName(),
            self.selectedFontSize(),
        )

        self.codeArea.setPlainText(dot)
        self.previewImage.setPixmap(self.render(dot))
        self.previewImage.resize(self.previewImage.pixmap().size())

    def copyDot(self):
        clipboard = QApplication.clipboard()
        clipboard.clear()
        clipboard.setText(self.codeArea.toPlainText())

    def copyPng(self):
        clipboard = QApplication.clipboard()
        clipboard.clear()
        clipboard.setPixmap(self.previewImage.pixmap())

    def accept(self):
        path = QFileDialog.getSaveFileName(
            self, "Save Graph Image", "graph.png", filter="PNG Image (*.png)"
        )[0]
        file = QFile(path)
        file.open(QIODevice.OpenModeFlag.WriteOnly)
        self.previewImage.pixmap().save(file, "png")
