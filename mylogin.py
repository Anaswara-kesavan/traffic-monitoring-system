import streamlit as st
import cv2 as cv
import tempfile
import numpy as np
import time
import smtplib
import os
from dotenv import load_dotenv
load_dotenv()
from time import sleep

st.title("Traffic Monitor")

Name = st.text_input("Name")
Email = st.text_input("Email")
Area = st.text_input("Area")

GMAIL_USER = os.getenv("gmail_user")
GMAIL_PASSWORD = os.getenv("gmail_pwd")
FROM = GMAIL_USER
server = smtplib.SMTP("smtp.gmail.com", 587)
server.ehlo()
server.starttls()
server.login(GMAIL_USER , GMAIL_PASSWORD )


if st.button("Login"):
    st.success("Logged In as {}".format(Name))
    min_contour_width = 40  # 40
    min_contour_height = 40  # 40
    offset = 10  # 10
    delay = 60
    line_height = 550  # 550
    detected_car = []
    cars = 0


    def get_centroid(x, y, w, h):
        x1 = int(w / 2)
        y1 = int(h / 2)

        cx = x + x1
        cy = y + y1
        return cx, cy



    subtract = cv.bgsegm.createBackgroundSubtractorMOG()
    vf = cv.VideoCapture('video.mp4')
    stframe = st.empty()
    vf.set(3, 640)
    vf.set(4, 480)
    frame_set = []
    start_time = time.time()

    while vf.isOpened():
        ret, frame = vf.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        tempo = float(1 / delay)
        grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(grey, (3, 3), 5)
        img = subtract.apply(blur)
        dilated = cv.dilate(img, np.ones((5, 5)))
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
        closing = cv.morphologyEx(dilated, cv.MORPH_CLOSE, kernel)
        closing = cv.morphologyEx(closing, cv.MORPH_CLOSE, kernel)
        contour, h = cv.findContours(closing, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        cv.line(frame, (25, line_height), (1200, line_height), (255, 127, 0), 3)
        for (i, c) in enumerate(contour):
            (x, y, w, h) = cv.boundingRect(c)
            valid_contour = (w >= min_contour_width) and (h >= min_contour_height)
            if not valid_contour:
                continue

            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            centroid = get_centroid(x, y, w, h)
            detected_car.append(centroid)
            cv.circle(frame, centroid, 4, (0, 0, 255), -1)

            for (x, y) in detected_car:
                if y < (line_height + offset) and y > (line_height - offset):
                    cars += 1
                    cv.line(frame, (25, line_height), (1200, line_height), (0, 127, 255), 3)
                    detected_car.remove((x, y))
                    end_time = time.time()
                    elapsed = end_time - start_time
                    if elapsed > 10:
                        if cars > 7:
                            x = "Traffic"
                            st.write('*HIGH TRAFFIC*')
                            st.write("Take a different route.....")
                            if x == "Traffic":
                                server.close()
                                st.stop()

                                TO = [Email]
                                SUBJECT = "Alert"
                                TEXT = "High Traffic.....Take a different route"

                                # Prepare actual message
                                message = """From: %s\nTo: %s\nSubject: %s\n\n%s
                                """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
                                server.sendmail(FROM, TO, message)

                        else:
                            x = "No"
                            st.write('*Low TRAFFIC*')
                            st.write("Take this route.....")
                            if x == "No":

                                TO = [Email]
                                SUBJECT = "Alert"
                                TEXT = "Low Traffic.....Take this route"
                                # Prepare actual message
                                message = """From: %s\nTo: %s\nSubject: %s\n\n%s
                                                              """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
                                server.sendmail(FROM, TO, message)


                                server.close()

                                st.stop()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        stframe.image(frame)


