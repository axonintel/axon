import time
import cbpro
import queue
import logging
import datetime
import json
from axonbot.axonwebsocket import AxonWebsocket


logging.basicConfig(filename='./bot.log')


class AxonBot:
    """
    A trader class that takes executes trades in coinbase pro by leverging axonbot websocket and cbpro.
    Allows daily trades to happen on coinbase pro by leveraging coinbasepro-python.
    conditions:
        self.connection_preparation_time + self.trade_window < self.axon_maximum_connection_duration
    """

    def __init__(self, cb_api_key="", cb_api_secret="", passphrase="",
                 axon_api_key="n1MLgSRxLP86iHUUjAFEv6PDC9NCWoVP5DBTAcN6",
                 connection_preparation_window=5, trading_window=60):

        # Initialize axonwebsocket, trader and queue to share between threads
        self.axon = None
        self.trader = None
        self.axon_queue = queue.Queue()

        # Initialize keys and logs
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.cb_api_key = cb_api_key
        self.cb_api_secret = cb_api_secret
        self.passphrase = passphrase
        self.axon_api_key = axon_api_key
        self.axon_maximum_connection_duration = 90


        # initialize trade parameters

        self.is_in_trading_window = False
        self.now = 0
        self.tsnow = 0
        self.forecast = None
        self.next_candle_to_trade = None
        self.connection_preparation_window = connection_preparation_window
        self.trading_window = trading_window

        # Initialize CB Pro account information
        self.btc_account = None
        self.usd_account = None

    def connect_to_axon(self):
        axon = AxonWebsocket(self.axon_queue, api_key=self.axon_api_key)
        axon.connect()
        while not axon.wsapp.sock.connected:
            time.sleep(1)
        self.log.info('Axon Websocket connected')
        return axon

    def get_latest_forecast(self):
        """
        Fetch the latest forecast form the queue of messages received from Axon's bot. Reconnect to Axon if needed.
        :return: True if successful and sets a dictionary of the latest forecast to use to self.
        """

        # Ensure only latest queue message is processed.
        if self.axon_queue.qsize() > 1:
            _ = self.axon_queue.get()

        # Get latest message from queue or block until a new notification is present
        new_msg = self.axon_queue.get()
        if new_msg == "websocket disconnected":
            time.sleep(3)
            self.axon = self.connect_to_axon()
            self.get_latest_forecast()
        elif "timestamp" in new_msg:
            self.forecast = new_msg
            return True

    def connect(self):
        """
        Allows bot to connect to Axon Websocket and to Coinbase pro and (1) start receiving notifications from Axon and
        (2) collect account information for both BTC and USD from coinbase pro.
        Since Axon is a daily trader at the time of the writing, it is assumed that the strategy initiates such
        connections self.connection_preparation_time (default = 5 minutes) prior to day close in UTC.
        WARNING: axon's websockets maximum connection duration is 90 minutes.
        """
        # Connect to both axon & coinbase pro
        self.axon = self.connect_to_axon()
        self.trader = cbpro.AuthenticatedClient(self.cb_api_key, self.cb_api_secret, self.passphrase)
        assert self.gather_account_information()
        assert self.get_latest_forecast()
        self.log.info('Coinbase Pro client connected')
        return True

    def checkif_in_trading_window(self, candle="1D"):
        assert self.connection_preparation_window + self.trading_window < self.axon_maximum_connection_duration
        self.now = datetime.datetime.utcnow()
        self.tsnow = int(time.time())
        if candle == "1D":
            if self.now.hour <= 1:
                if self.now.hour * 60 + self.now.minute < self.trading_window:
                    self.is_in_trading_window = True
                    self.next_candle_to_trade = self.now.strftime("%Y-%m-%d 00:00Z")
                    return True
            elif self.now.hour == 23:
                if self.now.minute % (60 - self.connection_preparation_window) < self.connection_preparation_window:
                    self.is_in_trading_window = True
                    self.next_candle_to_trade = (self.now + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00Z")
                    return True
            else:
                self.is_in_trading_window = False
                self.next_candle_to_trade = (self.now + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00Z")
                return False

    def gather_account_information(self):
        accounts = self.trader.get_accounts()

        try:
            self.btc_account = accounts[[account['currency'] for account in accounts].index('BTC')]
            self.usd_account = accounts[[account['currency'] for account in accounts].index('USD')]
            return True
        except Exception as e:
            self.log.debug(e)
            return False

    def run_daily_trading_strategy(self):

        self.checkif_in_trading_window()

        if self.is_time_to_trade:
            assert self.connect()
            forecast_candle = json.loads(self.forecast['forecast'])['candle']

            # Wait for the newest forecast to be added to the queue by Axon's websocket
            if self.next_candle_to_trade != forecast_candle:
                while self.axon_queue.qsize() == 0:
                    self.log.info("In trading window: Waiting for the latest update from Axon")
                    time.sleep(1)
                self.get_latest_forecast()
            self.log.info("A NEW forecast received: " + str(self.forecast))
            self.execute_trade()
        else:
            print("Not in trading window: sleeping for two minutes")
            time.sleep(120)

    def execute_trade(self):

        pass
        #TODO get current open positions
        #TODO compare forecast to open position
        #TODO execute trade if needed

