# Axon | AI AutoTrader
##### Provided under MIT License by Axon Intellex.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Benefits
- A simple to use python wrapper for automatic trading based on Axon's websocket.
- Allows daily trades to happen on coinbase pro by leveraging coinbasepro-python.
- Enhance your trading decisions by leveraging Axon's reinforcement learning gathered from tons of features from the market.

## Under Development
- Integration to coinbasepro-python **Looking for assistance**
- real-time order book

## Background
- Axon is an artificially intelligent agent that trades bitcoin for now. This module aims to connect to Axon's websocket and allow for instantanous AI-based trading decisions. 
- Axon's decisions are based on daily candles, the most important decision is taken when a daily candle closes and a new daily candle opens. 
- Axon runs an analysis, (_which may take up to 5 mins_), that estimates what the next course of action is for the freshly created daily candle. 
- All timing is assumed to be in UTC. **important**

### Axon's 3 Decisions:
1. Long: Taking a long position or buying with an anticipation of a minimum_roi
2. Short: Taking a short position or shorting with an anticipation of a minimum_roi
3. STFO: Staying the Fuck out or not trading due to either a sideway movement or high volatility and randomness in the market.

While the newly created daily candle's decision is less likely to change, the conclusion of the day that follows fluctuates more often and is very much driven by how the current daily candle shall close. Axon's websocket API updates the client every 30 minutes about its daily trading decisions. 

### To install:
```pip install axonbot```

### To upgrade to the latest version:
```pip install --no-cache-dir --upgrade axonbot```

#### To run in python:
```
from axonbot import AxonBot
bot = AxonBot(cb_api_key=CB_API_KEY, cb_api_secret=CB_API_SECRET, passphrase=CB_API_PASSPHRASE, axon_api_key=AXON_API_KEY)
bot.connect()
```
Returns True if connection to both Axon's websocket and CoinbasePro are successful.

*sample incomming message from Axon's websocket the day of 2021-09-26 00:00 UTC*
These messages are stored in a queue 
```
{
  "timestamp": 1632636034,
  "forecast": {
      "period": "1D",
      "candle": "2021-09-26 00:00 UTC",
      "decision": "STFO",
      "confidence": 0.5625,
      "minimum_roi": 0,
      "info": "Axon is staying the FUCK OUT | Confidence: 56.72%"
    }
  }
```
#### To check the status of your btc account:

```
bot.btc_account
```

returns

```
{
'id': 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx', 
'currency': 'BTC', 
'balance': '0.0100000000000000', 
'hold': '0.0000000000000000', 
'available': '0.01', 
'profile_id': 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx', 
'trading_enabled': True
}
```

#### To check the status of your usd account:

```
bot.usd_account
```

returns

```
{
'id': 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx', 
'currency': 'USD', 
'balance': '1000.0000000000000000', 
'hold': '0.0000000000000000', 
'available': '1000', 
'profile_id': 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx', 
'trading_enabled': True
}
```

#### Traiding window:
Since Axon trades daily, the bot has a traiding window that is 
capped by axon_maximum_connection_duration limit of 90 minutes such that:

```
connection_preparation_window + traiding_window < axon_maximum_connection_duration
```

To check if the bot is in the traiding window:

```
bot.checkif_in_traiding_window()
```


