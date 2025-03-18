import asyncio
import logging
import signal
from datetime import datetime
from funding_rate_aggregator import FundingRateAggregator
import os
import config

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

if __name__ == "__main__":
    asyncio.run(main()) 