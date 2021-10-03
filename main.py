import websocket
import json
import logging
import warnings
import time
from os import path

timestamp = int(time.time())


def on_message(wsapp, message):
    try:
        msg = json.loads(message)
        ts = msg['timestamp']
        print(msg) if is_new_message(ts) else print("Older forecast: ", msg)
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


def is_new_message(ts):
    """
    Compares timestamps of the incoming message from the websocket to determine if a new notification came in.
    Sets global timestamp to the newest incoming timestamp
    :param ts: integer  timestamp from incoming notification
    :return: True or False
    """
    global timestamp
    if ts > timestamp:
        timestamp = ts
        return True
    else:
        return False


if __name__ == "__main__":
    main()
