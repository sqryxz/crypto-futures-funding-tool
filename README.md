# Crypto Futures Funding Rate Aggregator

This tool aggregates and analyzes funding rates from major cryptocurrency derivatives exchanges (Binance and Deribit). It provides real-time monitoring and daily summaries of funding rates to help traders identify trends and opportunities.

## Features

- Real-time funding rate monitoring for Binance and Deribit
- Daily summaries with trend analysis
- Support for major cryptocurrency pairs
- Data persistence and historical analysis
- Configurable alerts for significant rate changes

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_api_secret
   DERIBIT_API_KEY=your_deribit_api_key
   DERIBIT_API_SECRET=your_deribit_api_secret
   ```
5. Run the main script:
   ```bash
   python3 main.py
   ```

## Configuration

The tool monitors the following pairs by default:
- BTC-USDT (Binance)
- ETH-USDT (Binance)
- BTC-PERPETUAL (Deribit)
- ETH-PERPETUAL (Deribit)

Additional pairs can be configured in the `config.py` file.

## Output

The tool provides:
1. Real-time funding rate updates in the console
2. Daily summary reports with trend analysis
3. Data storage in CSV format for historical analysis

## License

MIT License 