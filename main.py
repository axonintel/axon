import websocket
import json
import logging
import warnings
from os import path


def on_message(wsapp, message):
    try:
        msg = json.loads(message)
        print(msg)
    except Exception as e:
        print("Caught exception when converting message into json\n" + str(e))


def main():

    logging.basicConfig(format='{asctime} {name} {threadName} {levelname}: {message}', style='{', level=logging.INFO)
    warnings.filterwarnings("ignore")

    BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))  # (str): absolute path to project root

    uri = "wss://api.axonintellex.com"
    trial_key = "n1MLgSRxLP86iHUUjAFEv6PDC9NCWoVP5DBTAcN6"
    header = {"x-api-key":trial_key}
    wsapp = websocket.WebSocketApp(uri, on_message=on_message, header=header)
    wsapp.run_forever(ping_interval=60)


if __name__ == "__main__":
    main()
