import streamlit as st
import http.server
import socketserver
import threading
import os

st.set_page_config(page_title="Jupyter Book", layout="wide")

# Port lokal untuk menyajikan file statis Jupyter Book
PORT = 8000
BUILD_DIR = os.path.abspath("_build/html")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BUILD_DIR, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

# Jalankan server lokal satu kali di background
if "server_started" not in st.session_state:
    threading.Thread(target=start_server, daemon=True).start()
    st.session_state["server_started"] = True

# Tampilkan Jupyter Book melalui iframe local server
st.components.v1.iframe(f"http://localhost:{PORT}", height=900, scrolling=True)