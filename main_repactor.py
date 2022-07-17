import os
import sys
import time
import threading

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic

import PIL
import mouse
import pyautogui as ms


class main_repec(QtWidgets.QDialog):
    btn_disabled_Signal = QtCore.pyqtSignal()
    btn_enabled_Signal = QtCore.pyqtSignal()
    log_append_Signal = QtCore.pyqtSignal(str)
    process_bar_Signal = QtCore.pyqtSignal(int)
    reset_Signal = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QDialog.__init__(self, None)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(BASE_DIR+"\main.ui", self)

        self.page = 0
        self.file_name = None
        self.path = None
        self.cursor_point = None

        self.captureThread = False
        self.mouseThread = False

        self.file_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9a-zA-Z_/]*")))
        self.page_line.setValidator(QtGui.QIntValidator(self))

        self.cursor_set_button.clicked.connect(self.cursor_set)
        self.cursor_check_button.clicked.connect(self.cursor_check)
        self.brower_button.clicked.connect(self.fileopen)
        self.start_button.clicked.connect(self.active)
        
        self.btn_disabled_Signal.connect(self.button_disabled)
        self.btn_enabled_Signal.connect(self.button_enabled)
        self.log_append_Signal.connect(self.log_append)
        self.process_bar_Signal.connect(self.process_set)
        self.reset_Signal.connect(self.reset)

        QtWidgets.QMessageBox.information(self, "정보", "이 프로그램은 주모니터에서만 캡쳐가 가능합니다.\n듀얼모니터를 사용하는 사용자는 주모니터에서 캡쳐작업을 진행하시기 바랍니다.", QtWidgets.QMessageBox.Ok)
    
    def check_before_active(self):
        if self.page <= 0:
            return False
        if self.path == None:
            return False   
        if self.file_name == None:
            return False  
        if self.cursor_point == None:
            return False   
        return True

    def active(self):
        try:
            self.page = int(self.page_line.text())
        except:
            self.page = 0     
        finally:
            self.file_name = self.file_line.text()

        if not self.check_before_active():
            QtWidgets.QMessageBox.warning(self, "오류", "항목이 지정되지 않았습니다.", QtWidgets.QMessageBox.Ok)
            return

        self.path = "{0}/{1}.pdf".format(self.path_line.text(), self.file_name)
        if os.path.isfile(self.path):
            QtWidgets.QMessageBox.warning(self, "오류", "이미 파일이 존재합니다. 다른 파일명을 입력해주세요.", QtWidgets.QMessageBox.Ok)
            return

        self.log_append_Signal.emit("-------------------------------------------------------")
        self.log_append_Signal.emit("파일이름 : {0}".format(self.file_name))
        self.log_append_Signal.emit("페이지수 : {0}".format(self.page))
        self.log_append_Signal.emit("저장경로 : {0}".format(self.path))
        self.log_append_Signal.emit("커서위치 : {0}".format(self.cursor_point))
        self.log_append_Signal.emit("-------------------------------------------------------")

        self.btn_disabled_Signal.emit()
        
        QtWidgets.QMessageBox.information(self, "프로세스 시작", "캡쳐 진행 중 마우스 우클릭 시 프로그램이 멈추고\n이 때까지 저장된 캡쳐본을 pdf으로 저장합니다.\n확인을 누르면 캡쳐가 시작됩니다.", QtWidgets.QMessageBox.Ok)

        self.captureThread = True
        threading.Thread(target=self.capture).start()

        self.mouseThread = True
        threading.Thread(target=self.mouse_check).start()

    def capture(self):
        images = []
        
        ms.moveTo(self.cursor_point.x, self.cursor_point.y)
        ms.click(button = 'middle')

        while self.captureThread:
            if len(images) == self.page:
                self.mouseThread = False
                self.captureThread = False
                self.button_enabled()
                continue

            images.append(PIL.ImageGrab.grab())
            time.sleep(0.5)
            self.log_append_Signal.emit("{0} page complete".format(len(images)))

            percent = 100 / self.page * len(images)
            if percent >= 99:
                percent = 99
            self.process_bar_Signal.emit(percent)

            ms.moveTo(self.cursor_point.x, self.cursor_point.y)
            ms.click(button = 'left')
            time.sleep(1)

        self.process_bar_Signal.emit(99)      
        self.log_append_Signal.emit("Capture finish -> Make PDF...")

        time.sleep(1)
        images[0].save(self.path, save_all = True, append_images = images[1:])
        time.sleep(1)
        self.process_bar_Signal.emit(100)        
        self.log_append_Signal.emit("'{0}' Save!".format(self.path))
        self.log_append_Signal.emit("-------------------------------------------------------")
        self.reset_Signal.emit()

        

    def mouse_check(self):
        while self.mouseThread:
            if mouse.is_pressed("right"):            
                self.captureThread = False
                self.mouseThread = False    
                self.log_append_Signal.emit("Right Clicked! Process stop!")

    def cursor_set(self):           
        self.btn_disabled_Signal.emit()
        QtWidgets.QMessageBox.information(self, "설정", "확인을 누르고 다음페이지 버튼을 우클릭 하세요.", QtWidgets.QMessageBox.Ok)
        
        while True:
            if mouse.is_pressed("right"):
                self.cursor_point = ms.position()
                QtWidgets.QMessageBox.information(self, "설정", "커서위치 설정완료.", QtWidgets.QMessageBox.Ok)
                break
        
        self.btn_enabled_Signal.emit()       
        self.cursor_set_button.setText("재설정")

    def cursor_check(self):    
        ms.moveTo(self.cursor_point.x, self.cursor_point.y)
        QtWidgets.QMessageBox.information(self, "확인", "마우스 커서의 위치가 다음페이지 버튼위에 있는지 확인하세요.", QtWidgets.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def button_disabled(self):       
        self.cursor_set_button.setEnabled(False)
        self.cursor_check_button.setEnabled(False)
        self.file_line.setEnabled(False)
        self.page_line.setEnabled(False)
        self.brower_button.setEnabled(False)
        self.start_button.setEnabled(False)  

    @QtCore.pyqtSlot()
    def button_enabled(self):
        self.cursor_set_button.setEnabled(True)
        self.cursor_check_button.setEnabled(True)
        self.file_line.setEnabled(True)
        self.page_line.setEnabled(True)
        self.brower_button.setEnabled(True)
        self.start_button.setEnabled(True)
        
    @QtCore.pyqtSlot(str)
    def log_append(self, msg):        
        self.log_text.append(msg)

    @QtCore.pyqtSlot(int)
    def process_set(self, percent):
        if percent > 100:
            percent = 100
        self.process_bar.setValue(percent)

    @QtCore.pyqtSlot()
    def reset(self):        
        QtWidgets.QMessageBox.information(self, "완료", "'{0}' 경로에 저장완료.".format(self.path), QtWidgets.QMessageBox.Ok)

        self.page = 0
        self.file_name = None
        self.path = None
        self.cursor_point = None

        self.captureThread = False
        self.mouseThread = False

        self.process_bar_Signal.emit(0)        
        self.file_line.setText("")
        self.page_line.setText("0")
        self.cursor_set_button.setText("설정")
        self.path_line.setText("")
        self.button_enabled()

    def fileopen(self):
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self, '저장할 폴더')
        self.path_line.setText(self.path)

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = main_repec()
    main.show()
    app.exec_()