from smtplib import SMTP
import os
import streamlit as st
import cv2 as cv
import tempfile
import numpy as np
import time
from dotenv import load_dotenv, dotenv_values

# ✅ **Step 1: Load Environment Variables Properly**
env_path = "C:/Users/ASUS/PycharmProjects/pythonProject/email.env"  # Ensure correct path
load_dotenv(env_path)  # Load .env file

# Debugging: Print environment variables

# Debugging: Print environment variables (Hide password)
env_vars = dotenv_values(env_path)
env_vars["GMAIL_PASSWORD"] = "********"  # Hide password before printing
print("Loaded Environment Variables:", env_vars)



# ✅ Fetch credentials
GMAIL_USER = os.getenv("GMAIL_USER")  # Correct
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Correct



# 🚨 **Exit if credentials are missing**
if not GMAIL_USER or not GMAIL_PASSWORD:
    raise SystemExit("⚠️ ERROR: Environment variables not loaded! Check your .env file syntax.")

# ✅ **Step 2: Streamlit App UI**
st.title("Traffic Monitor")
Name = st.text_input("Name")
Email = st.text_input("Email").strip()  # Remove spaces

Area = ["thrithala"]
choice = st.selectbox("Area", Area)

# ✅ **Step 3: SMTP Email Setup**
try:
    server = SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    print("✅ Email login successful!")
except Exception as e:
    raise SystemExit(f"❌ Email login failed! Error: {e}")

# ✅ **Step 4: Traffic Monitoring Logic**
if st.button("Login"):
    st.success(f"Logged In as {Name}")

    # 🚗 Traffic Detection Parameters
    min_contour_width = 40
    min_contour_height = 40
    offset = 10
    delay = 60
    line_height = 550
    detected_car = []
    cars = 0


    def get_centroid(x, y, w, h):
        return x + int(w / 2), y + int(h / 2)


    subtract = cv.bgsegm.createBackgroundSubtractorMOG()

    uploaded_file = st.file_uploader("Upload a Traffic Video", type=["mp4", "avi", "mov"])

    if uploaded_file is not None and choice == "thrithala":
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            video_path = temp_file.name

        vf = cv.VideoCapture(video_path)
        stframe = st.empty()
        vf.set(3, 640)
        vf.set(4, 480)

        start_time = time.time()

        while vf.isOpened():
            ret, frame = vf.read()
            if not ret:
                break

            grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(grey, (3, 3), 5)
            img = subtract.apply(blur)
            dilated = cv.dilate(img, np.ones((5, 5)))
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
            closing = cv.morphologyEx(dilated, cv.MORPH_CLOSE, kernel)

            contour, _ = cv.findContours(closing, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            cv.line(frame, (25, line_height), (1200, line_height), (255, 127, 0), 3)

            for c in contour:
                x, y, w, h = cv.boundingRect(c)
                if w < min_contour_width or h < min_contour_height:
                    continue

                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                centroid = get_centroid(x, y, w, h)
                detected_car.append(centroid)
                cv.circle(frame, centroid, 4, (0, 0, 255), -1)

                for (cx, cy) in detected_car:
                    if (line_height - offset) < cy < (line_height + offset):
                        cars += 1
                        cv.line(frame, (25, line_height), (1200, line_height), (0, 127, 255), 3)
                        detected_car.remove((cx, cy))

                        elapsed = time.time() - start_time
                        if elapsed > 10:
                            if cars > 15:
                                st.warning("🚦 HIGH TRAFFIC: Take a different route!")

                                message = f"""From: {GMAIL_USER}\nTo: {Email}\nSubject: Traffic Alert\n\nHigh Traffic detected! Please take a different route."""
                                server.sendmail(GMAIL_USER, Email, message)
                                print("🚀 High Traffic Email Sent!")

                            else:
                                st.success("✅ LOW TRAFFIC: You can take this route.")

                                message = f"""From: {GMAIL_USER}\nTo: {Email}\nSubject: Traffic Alert\n\nLow Traffic detected. This route is clear."""
                                server.sendmail(GMAIL_USER, Email, message)
                                print("🚀 Low Traffic Email Sent!")

                            server.quit()  # Close SMTP
                            st.stop()

            stframe.image(frame, channels="BGR")



