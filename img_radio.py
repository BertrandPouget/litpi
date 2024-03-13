import streamlit as st
from streamlit_image_select import image_select
img = image_select(
    label="Select a cat",
    images=[
        "images/linkedin.jpg",
        "images/Fototessera.jpg",
    ],
    captions=["A cat", "Another cat"],
)

if img == "images/linkedin.jpg":
    st.write("You selected the first cat!")