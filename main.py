import websocket
import json
import logging
import warnings
import time
import datetime
from os import path

timestamp = int(time.time())


def on_message(wsapp, message):
    try:
        msg = json.loads(message)
        assert valid_axon_forecast(msg)

        if is_new_message(msg['timestamp']):
            print("TODO with a NEW notification came in: ", msg)
        else:
            print("TODO with an OLD notification after a websocket initial connect/re-connect", msg)
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

def valid_axon_forecast(msg):
    """
    Validates that the message follows axon's standards and has the information needed for decision making
    :param msg: json notification received by axon
    :return: True for valid and False for not valid or incomplete
    """
    ts = msg['timestamp']
    if ts:
        forecasts = json.loads(msg['forecast'])
        assert datetime.datetime.utcfromtimestamp(ts).replace(hour=0,minute=0,second=0) \
               == datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        assert forecasts[0]['candle'] == datetime.datetime.utcnow().strftime("%Y-%m-%d 00:00Z")
        assert forecasts[1]['candle'] == (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00Z")
        return True
    else:
        return False

if __name__ == "__main__":
    main()
