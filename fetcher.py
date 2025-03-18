import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class FundingRateFetcher:
    def __init__(self):
        self.binance_url = "https://fapi.binance.com/fapi/v1/fundingRate"
        self.deribit_url = "https://www.deribit.com/api/v2/public/get_funding_rate_value"
        
    async def fetch_binance_rates(self, symbols: List[str]) -> Dict:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in symbols:
                url = f"{self.binance_url}?symbol={symbol}"
                tasks.append(self.fetch_single_rate(session, url))
            return await asyncio.gather(*tasks)
    
    async def fetch_deribit_rates(self, instruments: List[str]) -> Dict:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for instrument in instruments:
                url = f"{self.deribit_url}?instrument_name={instrument}"
                tasks.append(self.fetch_single_rate(session, url))
            return await asyncio.gather(*tasks)

    async def fetch_single_rate(self, session: aiohttp.ClientSession, url: str) -> Dict:
        try:
            async with session.get(url) as response:
                data = await response.json()
                return self.normalize_rate_data(data)
        except Exception as e:
            logger.error(f"Error fetching rate: {e}")
            return None

    def normalize_rate_data(self, data: Dict) -> Dict:
        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': data.get('symbol'),
            'rate': float(data.get('fundingRate', 0)),
            'exchange': 'binance' if 'fundingRate' in data else 'deribit'
        }

    async def fetch_all_rates(self):
        binance_symbols = ['BTCUSDT', 'ETHUSDT']
        deribit_instruments = ['BTC-PERPETUAL', 'ETH-PERPETUAL']
        
        binance_rates = await self.fetch_binance_rates(binance_symbols)
        deribit_rates = await self.fetch_deribit_rates(deribit_instruments)
        
        # Filter out None values from failed requests
        all_rates = [rate for rate in (binance_rates + deribit_rates) if rate is not None]
        return all_rates 