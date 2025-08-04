import json
import queue
import threading

from streamlit.runtime.scriptrunner import add_script_run_ctx

from ws import *

if "websocket_thread" not in st.session_state:
    print("WebSocket thread not found")
    st.session_state.websocket_thread = None

if "websocket_connection" not in st.session_state:
    print("websocket_connection not found")
    st.session_state.websocket_connection = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_queue" not in st.session_state:
    st.session_state.message_queue = queue.Queue()

if st.session_state.websocket_thread is None or not st.session_state.websocket_thread.is_alive():
    print("Starting WebSocket connection...")
    websocket_thread = threading.Thread(target=run_websocket, daemon=True, args=('123',))
    add_script_run_ctx(websocket_thread)
    websocket_thread.start()
    st.session_state.websocket_thread = websocket_thread

st.title("Weather and places assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.websocket_connection.send(json.dumps({"question": prompt}))
    listen_response = True
    while listen_response:
        while not st.session_state.message_queue.empty():
            message = st.session_state.message_queue.get()
            json_message = json.loads(message)
            st.session_state.messages.append({"role": "assistant", "content": json_message['message']})
            with st.chat_message('assistant'):
                st.markdown(json_message['message'])
            listen_response = False
