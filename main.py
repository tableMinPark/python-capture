import os
import time
import threading

import pyautogui as ms
import PIL

class main:
    def __init__(self):
        # 클릭 수 = 페이지 수 - 1
        self.pages = int(input("페이지 수 >> "))
        self.path = "./pdf_files/" + input("파일명 입력 >> ") + ".pdf"

        while os.path.isfile(self.path):
            self.path = "./pdf_files/" + input("이미 파일명이 존재, 다른 파일명 입력 >> ") + ".pdf"

        if not os.path.isdir("pdf_files"):
            os.mkdir("./pdf_files")

        print(self.path)

        self.flag = True

    def active(self):
        self.capture(5)

    def capture(self, count=5):
        input("\n마우스를 '다음페이지' 버튼에 올리고 Enter (클릭금지)")
        

        self.button_position = ms.position()
        ms.moveTo(10, 10)
        ms.moveTo(self.button_position.x, self.button_position.y, 3)
        
        check = input("마우스 커서가 버튼위에 있으면 Enter")

        print("캡처가 {0}초 이후에 시작됩니다.".format(count))
        for sec in range(count, 0, -1):
            print("{0}초 뒤 시작".format(sec))
            time.sleep(1)            
        
        print("캡처를 시작합니다 마우스 움직이지 마세요!! (마우스 움직이면 캡처가 종료)")
       
        # 마우스 움직임 체크 쓰레드 시작
        threading.Thread(target=self.mouse_check).start()

        images = []

        for idx in range (0, self.pages):
            if not self.flag:
                break
            images.append(PIL.ImageGrab.grab())
            time.sleep(0.5)
            print("{0}page complete".format(idx + 1), end="")

            ms.click(button='left')
            print(" -> next page")
            time.sleep(1)
                    
        
        self.flag = False
    
    def mouse_check(self):
        while self.flag:
            if not self.button_position == ms.position():
                self.flag = False
                print("마우스가 움직였습니다.")
                for sec in range(5, 0, -1):
                    print("{0}초 뒤 종료".format(sec))
                    time.sleep(1)    
                os.remove(self.path)
                exit()


if __name__ == "__main__":
    exec = main()
    exec.active()
