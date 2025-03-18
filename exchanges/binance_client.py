from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging
from typing import Dict, List
import pandas as pd
from datetime import datetime

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        self.logger = logging.getLogger(__name__)

    def get_funding_rates(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch current funding rates for specified symbols
        """
        try:
            rates = {}
            for symbol in symbols:
                premium_index = self.client.futures_mark_price(symbol=symbol)
                funding_rate = float(premium_index['lastFundingRate'])
                rates[symbol] = funding_rate * 100  # Convert to percentage
            return rates
        except BinanceAPIException as e:
            self.logger.error(f"Error fetching Binance funding rates: {str(e)}")
            return {}

    def get_historical_funding_rates(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch historical funding rates for a symbol
        """
        try:
            rates = self.client.futures_funding_rate(symbol=symbol, limit=limit)
            df = pd.DataFrame(rates)
            df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')
            df['fundingRate'] = df['fundingRate'].astype(float) * 100
            return df
        except BinanceAPIException as e:
            self.logger.error(f"Error fetching historical funding rates: {str(e)}")
            return pd.DataFrame() 