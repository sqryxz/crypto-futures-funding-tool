from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
DERIBIT_API_KEY = os.getenv('DERIBIT_API_KEY')
DERIBIT_API_SECRET = os.getenv('DERIBIT_API_SECRET')

# Trading pairs configuration
BINANCE_PAIRS = ['BTCUSDT', 'ETHUSDT']
DERIBIT_PAIRS = ['BTC-PERPETUAL', 'ETH-PERPETUAL']

# Intervals and timeframes
UPDATE_INTERVAL = 60  # seconds
SUMMARY_INTERVAL = 24 * 60 * 60  # 24 hours in seconds

# Thresholds for alerts (in percentage)
FUNDING_RATE_THRESHOLDS = {
    'high': 0.01,  # 1%
    'low': -0.01,  # -1%
}

# Data storage configuration
DATA_DIR = 'data'
FUNDING_RATES_FILE = os.path.join(DATA_DIR, 'funding_rates.csv')
SUMMARY_FILE = os.path.join(DATA_DIR, 'daily_summaries.csv') 