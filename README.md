# Axon Websocket Client / Trader

## Introduction
Axon is an artificially intelligent agent that trades bitcoin. This API is aimed to connect to Axon's websocket and allow for instantanous trading decisions. 

Axon is trained using reinforcement learning and gathers tons of features from the market to estimate the favorable action to take in the following two days. Since its decisions are based on daily candles, the most important decision is taken when a daily candle closes and a new daily candle opens. At that point, Axon runs an analysis that estimates what its next course of action is for the freshly created daily candle. All timing is assumed to be in UTC.

Axon may take 3 decisions:
1- Long: Taking a long position or buying with an anticipation of a minimum_roi
2- Short: Taking a short position or shorting with an anticipation of a minimum_roi
3- STFO: Staying the Fuck out or not trading due to either a sideway movement or high volatility and randomness in the market.

While the newly created daily candle's decision is less likely to change, the conclusion of the day that follows fluctuates more often and is very much driven by how the current daily candle shall close.

Axon's websocket API updates the client every 30 minutes about its daily trading decisions. 

## Installation

Requires python3 and websocket client - future work will be added to integrate coinbase pro.
### To run:
`python3 main.py`

*sample output*

  `{
  "timestamp": 1632636034,
  "forecast": [{
      "period": "1D",
      "candle": "2021-09-26 00:00 UTC",
      "decision": "STFO",
      "confidence": 0.5625,
      "minimum_roi": 0,
      "info": "Axon is staying the FUCK OUT | Confidence: 56.72%"
    },
  {
      "period": "1D",
      "candle": "2021-09-27  00:00 UTC",
      "decision": "LONG",
      "confidence": 0.5625,
      "minimum_roi": 0.02,
      "info": "Axon is LONG | Confidence: 56.25%"
    }]
  }`
