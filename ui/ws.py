import logging
import os
from logging import getLogger

import streamlit as st
import websocket

app_logger = getLogger()
app_logger.addHandler(logging.StreamHandler())
app_logger.setLevel(logging.INFO)


def on_message(ws, message):
    app_logger.info(f"ws message: {message}")
    st.session_state.message_queue.put(message)


def on_error(ws, error):
    app_logger.info(f"ws error: {error}")


def on_close(ws, close_status_code, close_msg):
    app_logger.info("ws connection closed")


def on_open(ws):
    st.session_state.websocket_connection = ws
    app_logger.info("ws opened")


def run_websocket(thread_id: str):
    app_logger.info(f"Starting websocket on {os.environ.get('WS_PATH')}/{thread_id}")
    ws = websocket.WebSocketApp(
        f"{os.environ.get("WS_PATH")}/{thread_id}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()
