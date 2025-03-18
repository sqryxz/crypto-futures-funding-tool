# Crypto Futures Funding Rate Aggregator

This tool aggregates and analyzes funding rates from major cryptocurrency derivatives exchanges (Binance and Deribit). It provides real-time monitoring and daily summaries of funding rates to help traders identify trends and opportunities in the cryptocurrency futures markets.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output](#output)
- [API Documentation](#api-documentation)
- [Data Storage](#data-storage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-time funding rate monitoring for Binance and Deribit
- Daily summaries with trend analysis
- Support for major cryptocurrency pairs
- Data persistence and historical analysis
- Configurable alerts for significant rate changes
- Customizable monitoring intervals
- Export functionality for data analysis
- RESTful API for data access
- Detailed logging and error handling
- Email notifications for critical events

## Prerequisites

Before setting up the tool, ensure you have the following:

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Active accounts on Binance and Deribit with API access
- Basic understanding of cryptocurrency futures and funding rates

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crypto-futures-funding-tool.git
   cd crypto-futures-funding-tool
   ```

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
   
   # Optional email configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_specific_password
   NOTIFICATION_EMAIL=recipient@example.com
   ```

5. Run the main script:
   ```bash
   python3 main.py
   ```

## Configuration

The tool can be configured through the `config.py` file:

### Default Trading Pairs
- BTC-USDT (Binance)
- ETH-USDT (Binance)
- BTC-PERPETUAL (Deribit)
- ETH-PERPETUAL (Deribit)

### Customizable Parameters
- `MONITORING_INTERVAL`: Frequency of rate checks (default: 60 seconds)
- `ALERT_THRESHOLD`: Percentage change to trigger alerts (default: 0.01%)
- `DATA_RETENTION_DAYS`: Number of days to keep historical data (default: 90)
- `LOG_LEVEL`: Logging verbosity (default: INFO)

To add new trading pairs, edit the `TRADING_PAIRS` dictionary in `config.py`:
```python
TRADING_PAIRS = {
    'binance': ['BTC-USDT', 'ETH-USDT', 'SOL-USDT'],
    'deribit': ['BTC-PERPETUAL', 'ETH-PERPETUAL']
}
```

## Usage

### Basic Usage
```bash
# Start the monitoring tool
python3 main.py

# Start with custom config file
python3 main.py --config custom_config.py

# Run in debug mode
python3 main.py --debug
```

### Advanced Usage
```bash
# Generate historical analysis report
python3 main.py --analyze --days 30

# Export data to CSV
python3 main.py --export funding_rates.csv

# Run API server only
python3 main.py --api-only
```

## Output

The tool provides multiple output formats:

1. Real-time Console Updates:
   - Current funding rates
   - Rate changes and trends
   - Alert notifications

2. Daily Summary Reports:
   - Average daily rates
   - High/low values
   - Trend analysis
   - Volume information

3. Data Storage:
   - CSV files with timestamped entries
   - JSON export option
   - Database storage (optional)

## API Documentation

The tool provides a RESTful API for data access:

### Endpoints
- `GET /api/v1/rates`: Current funding rates
- `GET /api/v1/historical`: Historical data
- `GET /api/v1/summary`: Daily summaries
- `POST /api/v1/alerts`: Configure alerts

API documentation is available at `http://localhost:5000/docs` when running the API server.

## Data Storage

Data is stored in the following formats:

1. CSV Files:
   - `funding_rates.csv`: Raw funding rate data
   - `daily_summaries.csv`: Aggregated daily data

2. Database (Optional):
   - SQLite by default
   - Configurable for PostgreSQL

Data is stored in the `data/` directory by default.

## Troubleshooting

Common issues and solutions:

1. API Connection Issues:
   - Verify API keys are correct
   - Check internet connection
   - Ensure API endpoints are accessible

2. Data Collection Errors:
   - Check log files in `logs/`
   - Verify exchange status
   - Confirm rate limits

3. Performance Issues:
   - Adjust monitoring interval
   - Check system resources
   - Optimize data retention settings

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please ensure your code follows our style guide and includes appropriate tests.

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 