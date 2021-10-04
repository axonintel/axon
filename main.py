import websocket
import logging
import time
import json
from common.functions import valid_axon_forecast

# Initialize logger
logging.basicConfig(filename='./axon.log')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# capture timestamp
timestamp = int(time.time())


def on_message(wsapp, message):
    """
    :param wsapp: object - webscoket application
    :param message: string - received message
    :return: TODO returns trading decision and action taken based on the notification.
    """
    try:
        msg = json.loads(message)
        assert valid_axon_forecast(msg)

        if is_new_message(msg['timestamp']):
            LOGGER.info(message)
            print("TODO with a NEW notification came in: ", msg)
        else:
            LOGGER.info(message)
            print("TODO with an OLD notification after a websocket initial connect/re-connect", msg)
    except Exception as e:
        print("Caught exception when converting message into json\n" + str(e))


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


def main():

    uri = "wss://api.axonintellex.com"
    trial_key = "n1MLgSRxLP86iHUUjAFEv6PDC9NCWoVP5DBTAcN6"
    header = {"x-api-key":trial_key}
    wsapp = websocket.WebSocketApp(uri, on_message=on_message, header=header)
    wsapp.run_forever(ping_interval=60)


if __name__ == "__main__":
    main()
