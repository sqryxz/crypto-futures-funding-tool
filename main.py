import asyncio
import logging
import signal
from datetime import datetime
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
    def __init__(self, interval: int = 60):
        self.fetcher = FundingRateFetcher()
        self.analyzer = FundingRateAnalyzer()
        self.interval = interval  # Time between checks in seconds
        self.is_running = False
        
    async def start_monitoring(self):
        self.is_running = True
        logging.info("Starting funding rate monitoring...")
        
        while self.is_running:
            try:
                # Fetch rates
                rates = await self.fetcher.fetch_all_rates()
                
                # Analyze the new rates
                analysis = self.analyzer.analyze_rates(rates)
                
                # Log the results
                self._log_results(rates, analysis)
                
                # Store in database (assuming you have this implemented)
                await self._store_rates(rates)
                
                # Check for alerts
                if analysis['alerts']:
                    await self._handle_alerts(analysis['alerts'])
                
                # Wait for next interval
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait a bit before retrying
    
    def stop_monitoring(self):
        logging.info("Stopping monitoring...")
        self.is_running = False
    
    def _log_results(self, rates: List[Dict], analysis: Dict):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"\n=== Funding Rates Update ({current_time}) ===")
        for rate in rates:
            logging.info(f"{rate['exchange']} - {rate['symbol']}: {rate['rate']:.6f}")
        
        if analysis['alerts']:
            logging.info("\nAlerts:")
            for alert in analysis['alerts']:
                logging.info(f"⚠️ {alert['symbol']}: {alert['rate_change']:.2%} change")

    async def _store_rates(self, rates: List[Dict]):
        # Implement your database storage logic here
        pass

    async def _handle_alerts(self, alerts: List[Dict]):
        # Implement your alert handling logic here
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program terminated by user") 