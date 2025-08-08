# modules
import pandas as pd

# config
from src import config as cnf, session

from base import config as cnf
from base import session

class EMA(session.Session):
    # Constants
    TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
    EXCHANGE = "NSE"
    SYMBOL_TOKEN = "3045"

    def __init__(self):
        super().__init__()


    def get_historical_data(self, symbol, interval, duration):
        """Fetch historical data to calculate EMA."""

        historicDataParams = {
            "exchange": self.EXCHANGE,
            "symboltoken": symbol,
            "interval": interval,
            "fromdate": duration[0],  # Start date
            "todate": duration[1]    # End date
        }

        response = self.smart_api.getCandleData(historicDataParams)
        _candle_data = response['data']
        self.smart_api.terminateSession(cnf.CLIENT_ID)
        return pd.DataFrame(_candle_data, columns=["datetime", "open", "high", "low", "close", "volume"])

    def calculate_ema(self, data, period=21):
        """Calculate the 21 EMA."""
        data['EMA_21'] = data['close'].ewm(span=period, adjust=False).mean()
        return data

    def get_latest_close_greater_than_ema(self, _historical_data, time_interval, start_date, end_date):
        # _flag = None
        # try:
        _ema_data = self.calculate_ema(_historical_data)
        _ema_sorted = _ema_data.sort_values(by='EMA_21', ascending=True)
        print('+++ ema sorted \n\n', _ema_sorted)
        _greater_than = _ema_sorted[_ema_sorted['close'] > _ema_sorted['EMA_21']]
        print('+++ all greater than \n\n', _greater_than)
        last_row = _ema_sorted.iloc[-1]
        if last_row['close'] > last_row['EMA_21']:
            print("Condition met. Placing order because last close {} is greater than last ema_21 {}\n".format(
                last_row['close'], last_row['EMA_21']))

        _greater_last_row = _greater_than.iloc[-1]
        if _greater_last_row['close'] > _greater_last_row['EMA_21']:
            print("_greater_last_row : Condition met. Placing order because last close {} is greater than last ema_21 {}\n".format(
                _greater_last_row['close'], _greater_last_row['EMA_21']))

        # except Exception as e:
        #     print(f"Error fetching candle data: {str(e)}")
        # return _flag

# Strategy Execution
def main():
    start_date = "2024-01-01 09:15"
    end_date = "2024-02-01 15:30"
    time_interval = "ONE_DAY"
    ema = EMA()
    # token = session['data']['refreshToken']
    # print('+++ token ', token)
    # ema.smart_api.setAccessToken(token)
    # Fetch historical data for EMA calculation
    try:
        _historical_data = ema.get_historical_data(ema.SYMBOL_TOKEN, time_interval, [start_date, end_date])
        ema.get_latest_close_greater_than_ema(_historical_data, time_interval, start_date, end_date)
    except Exception as e:
        print(f"Error fetching candle data: {str(e)}")

if __name__ == "__main__":
    main()
