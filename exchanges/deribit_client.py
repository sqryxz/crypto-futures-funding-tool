import aiohttp
import asyncio
import logging
from typing import Dict, List
import pandas as pd
from datetime import datetime, timezone

class DeribitClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://www.deribit.com/api/v2"
        self.logger = logging.getLogger(__name__)

    async def _make_request(self, method: str, params: dict = None) -> dict:
        """
        Make authenticated request to Deribit API
        """
        url = f"{self.base_url}/{method}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Error {response.status}: {await response.text()}")
                        return {}
        except Exception as e:
            self.logger.error(f"Error making request to Deribit: {str(e)}")
            return {}

    async def get_funding_rates(self, instruments: List[str]) -> Dict[str, float]:
        """
        Fetch current funding rates for specified instruments using the ticker endpoint
        which provides real-time funding rate data
        """
        rates = {}
        for instrument in instruments:
            response = await self._make_request(
                "public/ticker",
                {"instrument_name": instrument}
            )
            if response.get("result"):
                # Get the current 8-hour funding rate
                funding_rate = response["result"].get("funding_8h", 0)
                rates[instrument] = float(funding_rate) * 100  # Convert to percentage
                
                # Log additional funding information for reference
                current_funding = response["result"].get("current_funding", 0)
                self.logger.debug(f"{instrument} - Current Funding: {current_funding}, 8h Rate: {funding_rate}")
        return rates

    async def get_funding_chart_data(self, instrument: str, length: str = "24h") -> pd.DataFrame:
        """
        Get funding rate chart data for visualization
        length options: 8h, 24h, 1m
        """
        response = await self._make_request(
            "public/get_funding_chart_data",
            {
                "instrument_name": instrument,
                "length": length
            }
        )
        if response.get("result"):
            data = response["result"].get("data", [])
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['interest_8h'] = df['interest_8h'].astype(float) * 100  # Convert to percentage
            return df
        return pd.DataFrame()

    async def get_historical_funding_rates(self, instrument: str, days: int = 30) -> pd.DataFrame:
        """
        Fetch historical funding rates for an instrument
        """
        current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        end_timestamp = current_timestamp
        start_timestamp = current_timestamp - (days * 24 * 60 * 60 * 1000)  # Convert days to milliseconds
        
        response = await self._make_request(
            "public/get_funding_rate_history",
            {
                "instrument_name": instrument,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp
            }
        )
        if response.get("result"):
            df = pd.DataFrame(response["result"])
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                # Convert interest rates to percentages
                for col in ['interest_1h', 'interest_8h']:
                    if col in df.columns:
                        df[col] = df[col].astype(float) * 100
            return df
        return pd.DataFrame()

    async def get_funding_rate_value(self, instrument: str, start_timestamp: int, end_timestamp: int) -> float:
        """
        Get the funding rate value for a specific time period
        """
        response = await self._make_request(
            "public/get_funding_rate_value",
            {
                "instrument_name": instrument,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp
            }
        )
        if response.get("result"):
            return float(response["result"]) * 100  # Convert to percentage
        return 0.0 