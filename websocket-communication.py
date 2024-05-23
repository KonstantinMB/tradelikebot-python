import requests
import time
import websocket
import json

# Feeding auth
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.binance.com'

def start_user_data_stream():
    url = f"{BASE_URL}/api/v3/userDataStream"
    headers = {'X-MBX-APIKEY': API_KEY}
    response = requests.post(url, headers=headers)
    return response.json()

def keep_user_data_stream_alive(listen_key):
    url = f"{BASE_URL}/api/v3/userDataStream?listenKey={listen_key}"
    headers = {'X-MBX-APIKEY': API_KEY}
    requests.put(url, headers=headers)

def on_message(ws, message):
    print("Received message:")
    print(json.loads(message))

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Stream opened.")

def websocket_app(listen_key):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{listen_key}",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    # Start user data stream
    response = start_user_data_stream()
    listen_key = response.get('listenKey')

    # Keep stream alive every 30 minutes
    while True:
        try:
            websocket_app(listen_key)
        except KeyboardInterrupt:
            break
        except:
            # Reconnect on errors
            time.sleep(10)
            continue
        finally:
            keep_user_data_stream_alive(listen_key)
            time.sleep(1800)  # Sleep for 30 minutes before sending keep-alive
