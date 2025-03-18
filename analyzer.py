import pandas as pd
import numpy as np
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FundingRateAnalyzer:
    def __init__(self, alert_threshold: float = 0.01):
        self.alert_threshold = alert_threshold

    def analyze_rates(self, rates: List[Dict]) -> Dict:
        if not rates:
            logger.warning("No rates to analyze")
            return {
                'statistics': {},
                'alerts': [],
                'arbitrage_opportunities': []
            }

        df = pd.DataFrame(rates)
        
        # Calculate basic statistics
        stats = {
            'mean_rate': df.groupby('symbol')['rate'].mean(),
            'std_dev': df.groupby('symbol')['rate'].std(),
            'min_rate': df.groupby('symbol')['rate'].min(),
            'max_rate': df.groupby('symbol')['rate'].max()
        }

        # Detect significant changes
        df['rate_change'] = df.groupby('symbol')['rate'].pct_change()
        significant_changes = df[abs(df['rate_change']) > self.alert_threshold]

        # Calculate arbitrage opportunities
        arb_opps = self._find_arbitrage_opportunities(df)

        return {
            'statistics': stats,
            'alerts': self._generate_alerts(significant_changes),
            'arbitrage_opportunities': arb_opps
        }

    def _find_arbitrage_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        opportunities = []
        
        # Group by timestamp to compare rates across exchanges
        for timestamp, group in df.groupby('timestamp'):
            for symbol in ['BTC', 'ETH']:
                binance_data = group[
                    (group['exchange'] == 'binance') & 
                    (group['symbol'].str.startswith(symbol))
                ]
                
                deribit_data = group[
                    (group['exchange'] == 'deribit') & 
                    (group['symbol'].str.startswith(symbol))
                ]
                
                if len(binance_data) == 0 or len(deribit_data) == 0:
                    continue
                
                binance_rate = binance_data['rate'].iloc[0]
                deribit_rate = deribit_data['rate'].iloc[0]
                
                spread = abs(binance_rate - deribit_rate)
                
                if spread > self.alert_threshold:
                    opportunities.append({
                        'timestamp': timestamp,
                        'symbol': symbol,
                        'spread': spread,
                        'binance_rate': binance_rate,
                        'deribit_rate': deribit_rate
                    })
        
        return opportunities

    def _generate_alerts(self, significant_changes: pd.DataFrame) -> List[Dict]:
        alerts = []
        for _, row in significant_changes.iterrows():
            alerts.append({
                'timestamp': row['timestamp'],
                'symbol': row['symbol'],
                'exchange': row['exchange'],
                'rate_change': row['rate_change'],
                'current_rate': row['rate']
            })
        return alerts

    def generate_daily_summary(self, historical_rates: List[Dict]) -> Dict:
        if not historical_rates:
            return {
                'period': {
                    'start': None,
                    'end': None
                },
                'summary_stats': {},
                'trend': {}
            }

        df = pd.DataFrame(historical_rates)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        return {
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'summary_stats': self.analyze_rates(historical_rates),
            'trend': self._analyze_trend(df)
        }

    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        trends = {}
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp')
            if len(symbol_data) >= 2:
                first_rate = symbol_data['rate'].iloc[0]
                last_rate = symbol_data['rate'].iloc[-1]
                trend = 'upward' if last_rate > first_rate else 'downward'
                trends[symbol] = {
                    'direction': trend,
                    'change': (last_rate - first_rate) / first_rate
                }
        return trends 