import websocket
import cbpro
import logging
import time
import json
import datetime


class AxonBot:
    """
    A simple to use python wrapper for automatic trading based on Axon's websocket.
    Allows daily trades to happen on coinbase pro by leveraging coinbasepro-python.
    Enhance your trading decisions by leveraging Axon's reinforcement learning gathered from tons of features from the market.

    Instance Variables:
        timestamp:  int - keeps track of system's time to compare and validate incoming websocket messages.
        socket:     websocekt object - a live websocket object that connects to Axon's api

    """

    def __init__(self):

        self.timestamp = int(time.time())

        # Initialize logger
        logging.basicConfig(filename='./axon.log')
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)

        # Initialize parameters
        self.uri = "wss://api.axonintellex.com"
        self.trial_key = "n1MLgSRxLP86iHUUjAFEv6PDC9NCWoVP5DBTAcN6"
        self.header = {"x-api-key": self.trial_key}
        self.ping_interval = 60
        self.wsapp = websocket.WebSocketApp(self.uri,
                                            on_message=self.on_message,
                                            on_close=on_websocket_close,
                                            header=self.header)
        self.cbpro = cbpro.PublicClient()

    def run(self):
        self.timestamp = int(time.time())
        self.wsapp.run_forever(ping_interval=self.ping_interval)

    def on_message(self, wsapp, message):
        """
        This is the main function in the class and where strategy should be built based on the latest notification from
        Axon. wsapp was added there to allow for the class websocket to be initialized
        :param message: string - received message
        :return: TODO returns trading decision and action taken based on the notification.
        """
        try:
            msg = json.loads(message)
            assert self.valid_axon_forecast(msg)

            if self.is_new_message(msg['timestamp']):
                self.log.info(message)
                self.notify("TODO with a NEW notification came in: " + message)
            else:
                self.log.info(message)
                self.notify("TODO with an OLD notification after a websocket initial connect/re-connect: " + message)
        except Exception as e:
            self.log.info("Caught exception when converting message into json\n" + str(e))
            self.notify("something went wrong, please check the logs")

    def valid_axon_forecast(self, msg):
        """
        Validates that the message follows axon's standards and has the information needed for decision making
        :param msg: json notification received by axon
        :return: True for valid and False for not valid or incomplete
        """
        ts = msg['timestamp']
        if ts:
            forecasts = json.loads(msg['forecast'])
            assert datetime.datetime.utcfromtimestamp(ts).replace(hour=0, minute=0,
                                                                  second=0) == datetime.datetime.utcnow() \
                       .replace(hour=0, minute=0, second=0, microsecond=0)
            assert forecasts[0]['candle'] == datetime.datetime.utcnow().strftime("%Y-%m-%d 00:00Z")
            assert forecasts[1]['candle'] == (datetime.datetime.utcnow()
                                              + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00Z")
            return True
        else:
            return False

    def is_new_message(self, ts):
        """
        Compares timestamps of the incoming message from the websocket to determine if a new notification came in.
        Sets class timestamp to the newest incoming timestamp
        :param ts: integer  timestamp from incoming notification
        :return: True or False
        """
        if ts > self.timestamp:
            self.timestamp = ts
            return True
        else:
            return False

    def notify(self, message):
        """
        Displays a message to the screen the same way print does.
        :param message: str - message to be displayed
        :return: prints out to user
        """
        print(message)


def on_websocket_close(wsapp, close_status_code, close_msg):
    if close_status_code == 1001 or close_status_code == 1000 or close_msg == "Going away":
        wsapp.sock = None
        wsapp.run_forever(ping_interval=60)
