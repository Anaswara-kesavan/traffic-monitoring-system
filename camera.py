import cv2
import numpy as np
import time
from time import sleep

st.title("""
         AI TRAFFIC CONTROL
         """
         )

start_time = time.time()
length_min = 80  # Largura inima do retangulo
height_min = 80  # Altura minima do retangulo

offset = 6  # Erro permitido entre pixel

pos_line = 550  # Posição da linha de contagem

delay = 60  # FPS do vídeo

detec = []
cars = 0


def pega_center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy
f = st.file_uploader("upload file")
try:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(f.read())
except:
    pass
capture_duration = 20


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()

    def __del__(self):
        self.video.releast()

    def get_frame(self):
        ret, frame1 = self.video.read()
        time = tempo = float(1 / delay)
        sleep(tempo)
        if frame1 is not None:
            grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(grey, (3, 3), 5)
            img_sub = subtracao.apply(blur)
            dilat = cv2.dilate(img_sub, np.ones((5, 5)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dilated = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
            dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
            contour, h = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.line(frame1, (25, pos_line), (1200, pos_line), (255, 127, 0), 3)
            for (i, c) in enumerate(contour):
                (x, y, w, h) = cv2.boundingRect(c)
                validar_contour = (w >= length_min) and (h >= height_min)
                if not validar_contour:
                    continue
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                center = pega_center(x, y, w, h)
                detec.append(center)
                cv2.circle(frame1, center, 4, (0, 0, 255), -1)
                for (x, y) in detec:
                    if y < (pos_line + offset) and y > (pos_line - offset):
                        cars += 1
                        cv2.line(frame1, (25, pos_line), (1200, pos_line), (0, 127, 255), 3)
                        detec.remove((x, y))
                        print("car is detected : " + str(cars))
                        cv2.putText(frame1, "VEHICLE COUNT : " + str(cars), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                    (0, 0, 255), 5)
                        break



                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()
