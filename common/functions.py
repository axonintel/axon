import json
import datetime


def valid_axon_forecast(msg):
    """
    Validates that the message follows axon's standards and has the information needed for decision making
    :param msg: json notification received by axon
    :return: True for valid and False for not valid or incomplete
    """
    ts = msg['timestamp']
    if ts:
        forecasts = json.loads(msg['forecast'])
        assert datetime.datetime.utcfromtimestamp(ts).replace(hour=0,minute=0,second=0) == datetime.datetime.utcnow()\
            .replace(hour=0, minute=0, second=0, microsecond=0)
        assert forecasts[0]['candle'] == datetime.datetime.utcnow().strftime("%Y-%m-%d 00:00Z")
        assert forecasts[1]['candle'] == (datetime.datetime.utcnow()
                                          + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00Z")
        return True
    else:
        return False
