import websocket
import logging
import time
import json
import datetime
from threading import Thread


logging.basicConfig(filename='./axon_websocket.log')


class AxonWebsocket:
    """
    A simple to use python wrapper for automatic trading based on Axon's websocket. Enhance your trading decisions by
     leveraging Axon's reinforcement learning gathered from tons of features from the market.

    Instance Variables:
        timestamp:  int - keeps track of system's time to compare and validate incoming websocket messages.
        socket:     websocekt object - a live websocket object that connects to Axon's api

    """

    def __init__(self, forecast_queue, api_key="n1MLgSRxLP86iHUUjAFEv6PDC9NCWoVP5DBTAcN6"):

        self.timestamp = int(time.time())

        # Initialize logger
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)

        # Initialize parameters
        self.uri = "wss://api.axonintellex.com"
        self.api_key = api_key
        self.header = {"x-api-key": self.api_key}
        self.ping_interval = 60
        self.time_out = 30
        self.wsapp = websocket.WebSocketApp(self.uri,
                                            on_message=self.on_message,
                                            on_close=self.on_websocket_close,
                                            header=self.header)
        self.forecast = None
        self.new_forecast = False
        self.thread = None
        self.qu = forecast_queue

    def connect(self):
        self.timestamp = int(time.time())
        self.thread = Thread(target=self.wsapp.run_forever, args=(None, None, self.ping_interval, self.time_out))
        self.thread.start()

    def on_message(self, wsapp, message):
        """
        This is the main function in the class and where strategy should be built based on the latest notification from
        Axon. wsapp was added there to allow for the class websocket to be initialized
        :param message: string - received message
        :return: puts a message in queue so it can be read by the creator of the object (example axonbot)
        """
        try:
            msg = json.loads(message)
            assert self.valid_axon_forecast(msg)
            self.forecast = msg

            if self.is_new_message(msg['timestamp']):
                self.new_forecast = True
                self.log.info("NEW notification came in: " + message)
            else:
                self.new_forecast = False
                self.log.info("OLD notification after a websocket initial connect/re-connect: " + message)
            # self.execute_strategy()
            self.qu.put(msg)
        except Exception as e:
            self.log.info("Caught exception when converting message into json\n" + str(e))

    def valid_axon_forecast(self, msg):
        """
        Validates that the message follows axon's standards and has the information needed for decision making
        :param msg: json notification received by axon
        :return: True for valid and False for not valid or incomplete
        """
        ts = msg['timestamp']
        if ts:
            forecast = json.loads(msg['forecast'])
            assert datetime.datetime.utcfromtimestamp(ts).replace(hour=0, minute=0,
                                                                  second=0) == datetime.datetime.utcnow() \
                       .replace(hour=0, minute=0, second=0, microsecond=0)
            assert forecast['candle'] == datetime.datetime.utcnow().strftime("%Y-%m-%d 00:00Z")
            # assert forecasts[1]['candle'] == (datetime.datetime.utcnow()
            #                                   + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00Z")
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

    def on_websocket_close(self, ws):
        self.qu.put("websocket disconnected")

