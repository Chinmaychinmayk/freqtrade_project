# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file


import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from freqtrade.strategy import IStrategy
from freqtrade.persistence import Trade


class BreakoutStrategy(IStrategy):
    """
    Breakout Strategy:
    - Long Entry: When price breaks above 20-bar high
    - Short Entry: When price breaks below 20-bar low
    - Stoploss: Based on 3-bar high/low with trailing
    - Only one trade open at a time
    """
    
    # Strategy settings
    timeframe = '1h'
    can_short = False
    use_custom_stoploss = True
    minimal_roi = {"0": 100}  # Effectively disable ROI-based exits
    stoploss = -0.99  # Wide initial stoploss, overridden by custom_stoploss
    
    # Ensures only one trade at a time
    max_open_trades = 1
    
    # These are required for all strategies
    process_only_new_candles = True
    startup_candle_count = 20  # Need at least 20 candles for indicators
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate technical indicators
        """
        # 20-bar high and low for breakout detection
        dataframe['high_20'] = dataframe['high'].rolling(20).max()
        dataframe['low_20'] = dataframe['low'].rolling(20).min()
        
        # 3-bar high and low for stoploss calculation
        dataframe['low_3'] = dataframe['low'].rolling(3).min()
        dataframe['high_3'] = dataframe['high'].rolling(3).max()
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define entry conditions
        """
        # Initialize columns
        dataframe.loc[:, 'enter_long'] = 0
        dataframe.loc[:, 'enter_short'] = 0
        
        # Long entry: Close breaks above previous 20-bar high
        dataframe.loc[
            (dataframe['close'] > dataframe['high_20'].shift(1)),
            'enter_long'
        ] = 1

        # Short entry: Close breaks below previous 20-bar low
        dataframe.loc[
            (dataframe['close'] < dataframe['low_20'].shift(1)),
            'enter_short'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define exit conditions - rely on custom stoploss
        """
        # Initialize columns
        dataframe.loc[:, 'exit_long'] = 0
        dataframe.loc[:, 'exit_short'] = 0
        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss based on 3-bar high/low with trailing capability
        """
        try:
            # Get dataframe for this pair
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            
            if dataframe is None or len(dataframe) < 3:
                return 0.99  # Return a wide stoploss if data is insufficient
                
            # Use the last completed candle
            last_candle = dataframe.iloc[-1]
            
            # Calculate stoploss price based on 3-bar high/low
            if trade.is_short:
                # For short trades, stoploss is above entry (use 3-bar high)
                stoploss_price = last_candle['high_3']
                # Calculate relative stoploss for short position
                relative_stoploss = (stoploss_price - current_rate) / current_rate
            else:
                # For long trades, stoploss is below entry (use 3-bar low)
                stoploss_price = last_candle['low_3']
                # Calculate relative stoploss for long position
                relative_stoploss = (stoploss_price - current_rate) / current_rate
            
            # Ensure stoploss is negative for long positions and positive for short positions
            return relative_stoploss
            
        except Exception as e:
            # Log the error for debugging
            self.logger.warning(f"Custom stoploss error for {pair}: {str(e)}")
            return 0.99  # Return a wide stoploss on error
