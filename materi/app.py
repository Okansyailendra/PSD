import streamlit as st

st.set_page_config(page_title="Proyek Sains Data", layout="wide")

# Hilangkan margin/padding bawaan Streamlit dan sembunyikan header
st.markdown("""
    <style>
        .main .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        iframe {
            width: 100% !important;
            height: 100vh !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

st.components.v1.iframe("/app/static/index.html", height=1000, scrolling=True)