import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List
import json

from exchanges.binance_client import BinanceClient
from exchanges.deribit_client import DeribitClient
import config

class FundingRateAggregator:
    def __init__(self):
        self.setup_logging()
        self.setup_storage()
        
        self.binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        self.deribit = DeribitClient(config.DERIBIT_API_KEY, config.DERIBIT_API_SECRET)
        
        self.funding_rates_df = pd.DataFrame()
        self.load_historical_data()

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_storage(self):
        """Setup data storage directory"""
        if not os.path.exists(config.DATA_DIR):
            os.makedirs(config.DATA_DIR)

    def load_historical_data(self):
        """Load historical funding rate data if it exists"""
        if os.path.exists(config.FUNDING_RATES_FILE):
            self.funding_rates_df = pd.read_csv(config.FUNDING_RATES_FILE)
            self.funding_rates_df['timestamp'] = pd.to_datetime(self.funding_rates_df['timestamp'])

    async def fetch_current_rates(self) -> Dict[str, float]:
        """Fetch current funding rates from all exchanges"""
        rates = {}
        
        # Fetch Binance rates
        binance_rates = self.binance.get_funding_rates(config.BINANCE_PAIRS)
        rates.update({f"binance_{k}": v for k, v in binance_rates.items()})
        
        # Fetch Deribit rates
        deribit_rates = await self.deribit.get_funding_rates(config.DERIBIT_PAIRS)
        rates.update({f"deribit_{k}": v for k, v in deribit_rates.items()})
        
        return rates

    async def fetch_24h_chart_data(self, instrument: str) -> pd.DataFrame:
        """Fetch 24-hour funding rate chart data for Deribit instruments"""
        if instrument in config.DERIBIT_PAIRS:
            return await self.deribit.get_funding_chart_data(instrument, length="24h")
        return pd.DataFrame()

    def update_data(self, rates: Dict[str, float]):
        """Update the funding rates dataframe with new data"""
        timestamp = datetime.now()
        new_data = pd.DataFrame({
            'timestamp': [timestamp],
            **{k: [v] for k, v in rates.items()}
        })
        
        self.funding_rates_df = pd.concat([self.funding_rates_df, new_data], ignore_index=True)
        self.funding_rates_df.to_csv(config.FUNDING_RATES_FILE, index=False)

    def generate_daily_summary(self, use_all_data: bool = False) -> str:
        """Generate a daily summary of funding rates"""
        if use_all_data:
            recent_data = self.funding_rates_df
        else:
            start_time = datetime.now() - timedelta(days=config.SUMMARY_START_DAYS)
            recent_data = self.funding_rates_df[self.funding_rates_df['timestamp'] > start_time]
        
        if recent_data.empty:
            return "No data available for analysis"

        summary = []
        summary.append("=== Funding Rate Summary ===")
        summary.append(f"Period: {recent_data['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')} to {recent_data['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Number of observations: {len(recent_data)}\n")
        
        for column in recent_data.columns:
            if column != 'timestamp':
                stats = recent_data[column].describe()
                summary.append(f"\n{column}:")
                summary.append(f"  Current: {recent_data[column].iloc[-1]:.4f}%")
                summary.append(f"  Period High: {stats['max']:.4f}%")
                summary.append(f"  Period Low: {stats['min']:.4f}%")
                summary.append(f"  Period Average: {stats['mean']:.4f}%")
                summary.append(f"  Period Std Dev: {stats['std']:.4f}%")
                
                # Calculate trend
                start_value = recent_data[column].iloc[0]
                end_value = recent_data[column].iloc[-1]
                trend = end_value - start_value
                trend_str = "↑" if trend > 0 else "↓" if trend < 0 else "→"
                summary.append(f"  Trend: {trend_str} ({trend:.4f}%)")
                
                # Calculate annualized yield
                avg_rate = stats['mean']
                annualized_yield = avg_rate * 365 * 3  # Assuming 3 funding payments per day
                summary.append(f"  Annualized Yield: {annualized_yield:.2f}%")
                
                # Add volatility indicator
                volatility = stats['std'] / abs(stats['mean']) if stats['mean'] != 0 else 0
                volatility_level = "Low" if volatility < 0.5 else "Medium" if volatility < 1.5 else "High"
                summary.append(f"  Rate Volatility: {volatility_level} ({volatility:.2f})")

        return "\n".join(summary)

    async def generate_exchange_comparison(self) -> str:
        """Generate a comparison of funding rates between exchanges"""
        comparison = []
        comparison.append("\n=== Exchange Funding Rate Comparison ===")
        
        # Get current rates
        rates = await self.fetch_current_rates()
        
        # Group by asset
        assets = {
            'BTC': {'binance': 'BTCUSDT', 'deribit': 'BTC-PERPETUAL'},
            'ETH': {'binance': 'ETHUSDT', 'deribit': 'ETH-PERPETUAL'}
        }
        
        for asset, pairs in assets.items():
            comparison.append(f"\n{asset}:")
            binance_rate = rates.get(f"binance_{pairs['binance']}", 0)
            deribit_rate = rates.get(f"deribit_{pairs['deribit']}", 0)
            spread = binance_rate - deribit_rate
            
            comparison.append(f"  Binance: {binance_rate:.4f}%")
            comparison.append(f"  Deribit: {deribit_rate:.4f}%")
            comparison.append(f"  Spread: {spread:.4f}%")
            
            # Arbitrage opportunity indicator
            if abs(spread) > config.FUNDING_RATE_THRESHOLDS['high']:
                comparison.append(f"  ⚠️ Potential arbitrage opportunity!")
        
        return "\n".join(comparison)

    async def run(self):
        """Main loop to fetch and process funding rates"""
        self.logger.info("Starting Funding Rate Aggregator...")
        
        while True:
            try:
                rates = await self.fetch_current_rates()
                self.update_data(rates)
                
                # Log current rates
                self.logger.info("\nCurrent Funding Rates:")
                for market, rate in rates.items():
                    self.logger.info(f"{market}: {rate:.4f}%")
                
                # Generate and log exchange comparison
                comparison = await self.generate_exchange_comparison()
                self.logger.info(comparison)
                
                # Generate summary every 5 minutes for demonstration
                if datetime.now().minute % 5 == 0:
                    summary = self.generate_daily_summary(use_all_data=True)
                    self.logger.info(f"\n{summary}")
                    
                    # Save summary to file
                    summary_file = os.path.join(config.DATA_DIR, 
                                              f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
                    with open(summary_file, 'w') as f:
                        f.write(summary)
                
                await asyncio.sleep(config.UPDATE_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying 