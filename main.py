import asyncio
import logging
import signal
from datetime import datetime, timedelta
from funding_rate_aggregator import FundingRateAggregator
import os
import config
from typing import Dict, List
from fetcher import FundingRateFetcher
from analyzer import FundingRateAnalyzer

# Global variable to store the aggregator instance
aggregator = None

def signal_handler(signum, frame):
    """Handle termination signals by generating a final summary"""
    logging.info("Received termination signal. Generating final summary...")
    if aggregator:
        # Generate the summary synchronously since we're in a signal handler
        summary = aggregator.generate_daily_summary(use_all_data=True)
        logging.info("\nFinal Daily Summary:\n" + summary)
        
        # Save the summary to a file
        summary_file = os.path.join(config.DATA_DIR, 
                                  f"final_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        logging.info(f"Final summary saved to: {summary_file}")
    
    # Exit gracefully
    exit(0)

async def main():
    global aggregator
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        aggregator = FundingRateAggregator()
        await aggregator.run()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        if aggregator:
            # Generate summary even on error
            summary = aggregator.generate_daily_summary(use_all_data=True)
            logging.info("\nFinal Daily Summary (on error):\n" + summary)
        raise

class FundingRateMonitor:
    def __init__(self, fetch_interval: int = 600, analysis_interval: int = 10800):
        self.fetcher = FundingRateFetcher()
        self.analyzer = FundingRateAnalyzer()
        self.fetch_interval = fetch_interval  # Time between fetches in seconds (600s = 10min)
        self.analysis_interval = analysis_interval  # Time between analysis in seconds (10800s = 3h)
        self.is_running = False
        self.stored_rates = []
        self.last_analysis_time = None
        
    async def start_monitoring(self):
        self.is_running = True
        self.last_analysis_time = datetime.now()
        logging.info("Starting funding rate monitoring...")
        logging.info(f"Fetch interval: {self.fetch_interval} seconds")
        logging.info(f"Analysis interval: {self.analysis_interval} seconds")
        
        while self.is_running:
            try:
                # Fetch rates
                rates = await self.fetcher.fetch_all_rates()
                if rates:
                    self.stored_rates.extend(rates)
                    # Log the fetched rates
                    self._log_fetch_results(rates)
                
                # Check if it's time for analysis (every 3 hours)
                current_time = datetime.now()
                if self.last_analysis_time is None or \
                   (current_time - self.last_analysis_time).total_seconds() >= self.analysis_interval:
                    
                    if self.stored_rates:
                        # Perform analysis
                        analysis = self.analyzer.analyze_rates(self.stored_rates)
                        self._log_analysis_results(analysis)
                        
                        # Handle alerts if any
                        if analysis['alerts']:
                            await self._handle_alerts(analysis['alerts'])
                        
                        # Update last analysis time
                        self.last_analysis_time = current_time
                        
                        # Clear stored rates after analysis
                        self.stored_rates = []
                    else:
                        logging.warning("No data available for analysis")
                
                # Wait for next fetch interval
                await asyncio.sleep(self.fetch_interval)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait a bit before retrying
    
    def stop_monitoring(self):
        logging.info("Stopping monitoring...")
        self.is_running = False
    
    def _log_fetch_results(self, rates: List[Dict]):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"\n=== Funding Rates Fetch ({current_time}) ===")
        for rate in rates:
            logging.info(f"{rate['exchange']} - {rate['symbol']}: {rate['rate']:.6f}")

    def _log_analysis_results(self, analysis: Dict):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"\n=== Analysis Results ({current_time}) ===")
        
        # Log statistics
        logging.info("\nStatistics:")
        for metric, values in analysis['statistics'].items():
            logging.info(f"{metric}:")
            for symbol, value in values.items():
                logging.info(f"  {symbol}: {value:.6f}")
        
        # Log alerts
        if analysis['alerts']:
            logging.info("\nAlerts:")
            for alert in analysis['alerts']:
                logging.info(f"⚠️ {alert['symbol']}: {alert['rate_change']:.2%} change")
        
        # Log arbitrage opportunities
        if analysis['arbitrage_opportunities']:
            logging.info("\nArbitrage Opportunities:")
            for opp in analysis['arbitrage_opportunities']:
                logging.info(f"💰 {opp['symbol']}: {opp['spread']:.6f} spread "
                          f"(Binance: {opp['binance_rate']:.6f}, "
                          f"Deribit: {opp['deribit_rate']:.6f})")

    async def _handle_alerts(self, alerts: List[Dict]):
        # Implement your alert handling logic here
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program terminated by user") 