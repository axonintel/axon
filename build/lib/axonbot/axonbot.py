import time
import cbpro
import queue
import logging
import datetime
from axonbot.axonwebsocket import AxonWebsocket

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG,
                    filename='./axonbot.log')


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
        self.new_forecast_executed = False
        self.current_position = None
        self.sides = {
            "long": "buy",
            "short": "sell",
            "stfo": "sell"
        }
        self.connection_preparation_window = connection_preparation_window
        self.trading_window = trading_window

        # Initialize CB Pro account information
        self.btc_account = None
        self.usd_account = None
        self.order = None

    def connect_to_axon(self):
        try:
            if self.axon.wsapp.sock.connected:
                return self.axon
        except:
            pass
        axon = AxonWebsocket(self.axon_queue, api_key=self.axon_api_key)
        axon.connect()
        if axon is None:
            self.log.info('Axon Websocket not created properly, retrying in 3 seconds')
            time.sleep(3)
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
        if new_msg == "websocket_disconnected":
            time.sleep(3)
            self.axon = self.connect_to_axon()
            self.get_latest_forecast()
            return True
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
                    self.next_candle_to_trade = self.now.strftime("%Y-%m-%d")
                    return True
                else:
                    self.is_in_trading_window = False
                    self.next_candle_to_trade = (self.now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    return False
            elif self.now.hour == 23:
                if self.now.minute % (60 - self.connection_preparation_window) < self.connection_preparation_window:
                    self.is_in_trading_window = True
                    self.next_candle_to_trade = (self.now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    return True
                else:
                    self.is_in_trading_window = False
                    self.new_forecast_executed = False
                    self.next_candle_to_trade = (self.now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    return False
            else:
                self.is_in_trading_window = False
                self.new_forecast_executed = False
                self.next_candle_to_trade = (self.now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                return False

    def gather_account_information(self):
        accounts = self.trader.get_accounts()

        try:
            self.btc_account = accounts[[account['currency'] for account in accounts].index('BTC')]
            self.usd_account = accounts[[account['currency'] for account in accounts].index('USD')]
            btc_price = float(self.trader.get_product_ticker('BTC-USD')['price'])
            if float(self.btc_account['balance']) * btc_price > float(self.usd_account['balance']):
                self.current_position = 'long'
            else:
                self.current_position = 'short'
            return True
        except Exception as e:
            self.log.debug(e)
            return False

    def run_daily_trading_strategy(self):
        while True:
            self.checkif_in_trading_window()

            if self.is_in_trading_window and not self.new_forecast_executed:
                assert self.connect()
                self.get_latest_forecast()
                forecast_candle = self.forecast['forecast']['candle']

                # Wait for the newest forecast to be added to the queue by Axon's websocket
                while self.next_candle_to_trade != forecast_candle:
                    self.log.info("In trading window: Waiting for the latest forecast from Axon's websocket")
                    while self.axon_queue.qsize() == 0:
                        time.sleep(1)
                    self.get_latest_forecast()
                    forecast_candle = self.forecast['forecast']['candle']
                self.log.info("A NEW forecast received: %s", str(self.forecast))
                self.execute_trade()
            else:
                next_candle_to_trade_dt = datetime.datetime.strptime(self.next_candle_to_trade, "%Y-%m-%d")
                sleep_for = (next_candle_to_trade_dt - self.now).seconds - self.connection_preparation_window * 60 + 1
                sleep_for = max(1, sleep_for)
                if self.new_forecast_executed:
                    self.log.info("New forecast already executed: sleeping for %s seconds", str(sleep_for))
                else:
                    self.log.info("Not in trading window: sleeping for %s seconds", str(sleep_for))
                time.sleep(sleep_for)
                self.new_forecast_executed = False

    def execute_trade(self):
        self.order = None
        orders = self.trader.get_orders()
        if len(list(orders)) > 0:
            self.trader.cancel_all(product_id='BTC-USD')

        new_decision = self.forecast['forecast']['decision']
        if self.current_position == 'long' and new_decision in ['short', 'stfo']:
            side = 'sell'
            self.order = self.trader.place_market_order(product_id='BTC-USD', side=side,
                                                        size=float(self.btc_account['balance']))
            self.log.info("Short position placed. Order: %s", str(self.order))
            while self.order['status'] != 'done':
                while 'status' not in self.trader.get_order(self.order['id']):
                    self.log.info("Waiting on Coinbase pro updates")
                    time.sleep(3)
                self.order = self.trader.get_order(self.order['id'])
            self.new_forecast_executed = True
            self.log.info("Short position executed. Order: %s", str(self.order))
        elif self.current_position == 'short' and new_decision == 'long':
            side = 'buy'
            self.order = self.trader.place_market_order(product_id='BTC-USD', side=side,
                                                        funds=round(float(self.usd_account['balance']), 2))
            self.log.info("Long position placed. Order: %s", str(self.order))
            while self.order['status'] != 'done':
                while 'status' not in self.trader.get_order(self.order['id']):
                    self.log.info("Waiting on Coinbase pro updates")
                    time.sleep(3)
                self.order = self.trader.get_order(self.order['id'])
            self.new_forecast_executed = True
            self.log.info("Long position executed. Order: %s", str(self.order))
        else:
            self.log.info("No action taken. Current position is %s. Newest Axon decision is: %s",
                          str(self.current_position), str(new_decision))
            self.new_forecast_executed = True


