import os, sys

from PyQt5.QtGui import QFont, QIcon

from loadingLbl import LoadingLabel
from script import SpeechProcessorWrapper, generate_random_string, open_directory

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QTextEdit, QWidget, QMessageBox

from PyQt5.QtCore import QThread, QCoreApplication, Qt, pyqtSignal

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support

QApplication.setFont(QFont('Arial', 12))
QApplication.setWindowIcon(QIcon('logo.svg'))


class Thread(QThread):
    afterGenerated = pyqtSignal(str)

    def __init__(self, wrapper: SpeechProcessorWrapper, text: str):
        super(Thread, self).__init__()
        self.__wrapper = wrapper
        self.__text = text

    def run(self):
        try:
            filename = f'{generate_random_string(10)}.wav'
            self.__wrapper.convert_text_into_audio(self.__text, filename=filename)
            self.afterGenerated.emit(filename)
        except Exception as e:
            raise Exception(e)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__wrapper = SpeechProcessorWrapper()
        self.__wrapper.init_process()

    def __initUi(self):
        self.setWindowTitle('Speech')

        self.__textEdit = QTextEdit()
        self.__textEdit.setPlaceholderText('Input the text...')
        self.__textEdit.textChanged.connect(self.__textChanged)
        self.__textEdit.setAcceptRichText(False)

        self.__btn = QPushButton('Run')
        self.__btn.clicked.connect(self.__run)
        self.__btn.setEnabled(False)

        self.__loadingLbl = LoadingLabel()
        self.__loadingLbl.setVisible(False)

        lay = QVBoxLayout()
        lay.addWidget(self.__textEdit)
        lay.addWidget(self.__btn)
        lay.addWidget(self.__loadingLbl)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

    def __textChanged(self):
        self.__btn.setEnabled(self.__textEdit.toPlainText().strip() != '')

    def __run(self):
        try:
            self.__t = Thread(wrapper=self.__wrapper, text=self.__textEdit.toPlainText())
            self.__t.started.connect(self.__started)
            self.__t.afterGenerated.connect(self.__afterGenerated)
            self.__t.finished.connect(self.__finished)
            self.__t.start()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def __started(self):
        print('started')
        self.__btn.setEnabled(False)
        self.__loadingLbl.start()
        self.__loadingLbl.setVisible(True)

    def __afterGenerated(self, filename):
        open_directory(filename)

    def __finished(self):
        print('finished')
        self.__btn.setEnabled(True)
        self.__loadingLbl.stop()
        self.__loadingLbl.setVisible(False)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())