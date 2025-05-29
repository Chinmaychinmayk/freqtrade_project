from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import talib.abstract as ta
from datetime import datetime
import logging

try:
    from freqtrade.exchange.common import stoploss_from_absolute
except ImportError:
    def stoploss_from_absolute(stoploss_price: float, current_rate: float, is_short: bool = False) -> float:
        """
        Calculate stoploss percentage from absolute price.
        """
        if is_short:
            return (current_rate - stoploss_price) / current_rate
        return (stoploss_price - current_rate) / current_rate

# Configure logging
logger = logging.getLogger(__name__)

class PairBreakoutStrategy(IStrategy):
    timeframe = '1h'
    can_short = False  # Spot market compatibility
    use_custom_stoploss = True
    minimal_roi = {"0": 100}  # Disable ROI-based exits
    stoploss = -0.99  # Wide initial stoploss, overridden by custom_stoploss

    @informative('1h', 'BTC/{stake}', fmt='{base}_{column}_{timeframe}')
    def populate_indicators_btc(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        logger.debug(f"BTC/USDT columns: {dataframe.columns.tolist()}")
        dataframe['high_20'] = dataframe['high'].rolling(20).max()
        dataframe['low_20'] = dataframe['low'].rolling(20).min()
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        logger.debug(f"ETH/USDT columns: {dataframe.columns.tolist()}")
        dataframe['low_3'] = dataframe['low'].rolling(3).min()
        dataframe['high_3'] = dataframe['high'].rolling(3).max()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        logger.debug(f"DataFrame columns in populate_entry_trend: {dataframe.columns.tolist()}")
        # Direct access to BTC_close_1h, as it's confirmed present
        dataframe['enter_long'] = (dataframe['btc_close_1h'] > dataframe['btc_high_20_1h'].shift(1)).astype(int)
        dataframe['enter_short'] = 0  # Disable short entries
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe  # Rely on stoploss for exits

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, after_fill: bool, **kwargs) -> float | None:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if after_fill:
            stoploss_price = dataframe['low'].iloc[-3:].min()
        else:
            last_candle = dataframe.iloc[-1].squeeze()
            stoploss_price = last_candle['low_3']
        return stoploss_from_absolute(stoploss_price, current_rate, is_short=False)