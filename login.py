import streamlit as st
import cv2 as cv

def main():
    """Simple Login App"""

    st.title("Simple Login App")

    Area = ["pattampi", "thrithala"]
    choice = st.selectbox("Area", Area)

    if choice == "pattampi":
        vf = cv.VideoCapture('video.mp4')

    elif choice == "Login":
        vf = cv.VideoCapture('cars')

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')

        if st.sidebar.button("Login"):
            st.success(f"Logged In as {username}")

    elif choice == "signup":
        st.subheader("Create New Account")

if __name__ == "__main__":
    main()
