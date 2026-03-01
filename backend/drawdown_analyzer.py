"""
Drawdown Analyzer for PA Investment Platform
============================================
Analyze drawdowns and correlate with news/events.

Features:
- Find drawdown periods in equity curves
- Fetch news headlines for date ranges via NewsAPI
- Match drawdowns with news events

Reference: NewsAPI.org for news data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import warnings

try:
    from config import settings
except ImportError:
    settings = None


class DrawdownAnalyzer:
    """
    Analyze drawdowns and correlate with news events.
    
    Methods:
    - find_drawdown_periods(): Identify drawdowns > threshold
    - get_news_for_period(): Fetch headlines via NewsAPI
    - correlate_events(): Match drawdowns with news
    """
    
    def __init__(self, news_api_key: str = None):
        """
        Initialize the drawdown analyzer.
        
        Args:
            news_api_key: NewsAPI key (optional - will use settings if not provided)
        """
        self.news_api_key = news_api_key or (settings.NEWS_API_KEY if settings else None)
        self.news_base_url = "https://newsapi.org/v2"
    
    def find_drawdown_periods(self, equity_curve: pd.Series, 
                               threshold: float = -0.05) -> pd.DataFrame:
        """
        Identify drawdown periods greater than threshold.
        
        Args:
            equity_curve: Series of portfolio values indexed by date
            threshold: Drawdown threshold (default -5%)
            
        Returns:
            DataFrame with columns: [start_date, end_date, peak, trough, drawdown]
        """
        if not isinstance(equity_curve, pd.Series):
            raise ValueError("equity_curve must be a pandas Series")
        
        # Handle empty or short series
        if len(equity_curve) < 2:
            return pd.DataFrame(columns=['start_date', 'end_date', 'peak', 'trough', 'drawdown'])
        
        # Calculate running maximum
        running_max = equity_curve.cummax()
        
        # Calculate drawdown at each point
        drawdown = (equity_curve - running_max) / running_max
        
        # Find drawdown periods
        in_drawdown = drawdown < threshold
        drawdown_periods = []
        
        # Track current drawdown period
        current_period = None
        
        for date, dd in drawdown.items():
            if dd < threshold and current_period is None:
                # Start new drawdown
                current_period = {
                    'start_date': date,
                    'peak_date': running_max.idxmax() if running_max.loc[:date].idxmax() else date,
                    'peak': running_max.loc[:date].max(),
                    'trough': equity_curve.loc[date],
                    'trough_date': date,
                    'min_drawdown': dd
                }
            elif dd < threshold and current_period is not None:
                # Continue drawdown
                if dd < current_period['min_drawdown']:
                    current_period['trough'] = equity_curve.loc[date]
                    current_period['trough_date'] = date
                    current_period['min_drawdown'] = dd
            elif dd >= threshold and current_period is not None:
                # End drawdown period
                current_period['end_date'] = date
                drawdown_periods.append(current_period)
                current_period = None
        
        # Handle ongoing drawdown at end
        if current_period is not None:
            current_period['end_date'] = equity_curve.index[-1]
            drawdown_periods.append(current_period)
        
        # Create DataFrame
        if not drawdown_periods:
            return pd.DataFrame(columns=['start_date', 'end_date', 'peak', 'trough', 'drawdown'])
        
        df = pd.DataFrame(drawdown_periods)
        df['drawdown'] = df['min_drawdown']
        
        return df[['start_date', 'end_date', 'peak', 'trough', 'drawdown']]
    
    def get_news_for_period(self, start_date: datetime, end_date: datetime,
                           query: str = "stock market", 
                           language: str = 'en') -> pd.DataFrame:
        """
        Fetch news headlines for a date range using NewsAPI.
        
        Args:
            start_date: Start date for news search
            end_date: End date for news search
            query: Search query (default: "stock market")
            language: Language filter (default: 'en')
            
        Returns:
            DataFrame with columns: [date, title, description, source, url]
        """
        if not self.news_api_key:
            warnings.warn("NewsAPI key not configured. Returning empty DataFrame.")
            return pd.DataFrame(columns=['date', 'title', 'description', 'source', 'url'])
        
        # Format dates for NewsAPI
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Build request URL
        url = f"{self.news_base_url}/everything"
        params = {
            'apiKey': self.news_api_key,
            'q': query,
            'from': from_date,
            'to': to_date,
            'language': language,
            'sortBy': 'publishedAt',
            'pageSize': 100
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'ok':
                warnings.warn(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return pd.DataFrame(columns=['date', 'title', 'description', 'source', 'url'])
            
            articles = data.get('articles', [])
            
            # Parse articles
            news_data = []
            for article in articles:
                published_at = article.get('publishedAt', '')
                try:
                    date = pd.to_datetime(published_at).date()
                except:
                    date = None
                
                news_data.append({
                    'date': date,
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', '')
                })
            
            return pd.DataFrame(news_data)
            
        except requests.exceptions.RequestException as e:
            warnings.warn(f"Error fetching news: {e}")
            return pd.DataFrame(columns=['date', 'title', 'description', 'source', 'url'])
    
    def correlate_events(self, equity_curve: pd.Series,
                        query: str = "stock market",
                        threshold: float = -0.05) -> Dict:
        """
        Match drawdowns with news events.
        
        Args:
            equity_curve: Series of portfolio values
            query: Search query for news
            threshold: Drawdown threshold
            
        Returns:
            Dictionary with drawdowns and associated news
        """
        # Find drawdown periods
        drawdowns = self.find_drawdown_periods(equity_curve, threshold)
        
        if drawdowns.empty:
            return {
                'drawdown_periods': drawdowns,
                'news_by_period': []
            }
        
        # Get news for each drawdown period
        news_by_period = []
        
        for _, row in drawdowns.iterrows():
            start = pd.to_datetime(row['start_date'])
            end = pd.to_datetime(row['end_date'])
            
            # Extend search window slightly
            search_start = start - timedelta(days=3)
            search_end = end + timedelta(days=1)
            
            news = self.get_news_for_period(search_start, search_end, query)
            
            news_by_period.append({
                'period': {
                    'start': start,
                    'end': end,
                    'drawdown': row['drawdown']
                },
                'news': news
            })
        
        return {
            'drawdown_periods': drawdowns,
            'news_by_period': news_by_period
        }
    
    def generate_report(self, equity_curve: pd.Series,
                       benchmark_curve: pd.Series = None,
                       query: str = "stock market") -> str:
        """
        Generate a text report of drawdown analysis.
        
        Args:
            equity_curve: Strategy equity curve
            benchmark_curve: Optional benchmark for comparison
            query: News search query
            
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("DRAWDOWN ANALYSIS REPORT")
        lines.append("=" * 60)
        
        # Calculate overall metrics
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        max_dd = drawdown.min()
        
        lines.append(f"\nMaximum Drawdown: {max_dd:.2%}")
        lines.append(f"Total Periods: {len(equity_curve)} days")
        
        # Find drawdowns
        drawdowns = self.find_drawdown_periods(equity_curve, threshold=-0.02)
        
        if not drawdowns.empty:
            lines.append(f"\nSignificant Drawdowns (>2%): {len(drawdowns)}")
            
            for i, row in drawdowns.head(5).iterrows():
                lines.append(f"\n  Period: {row['start_date'].strftime('%Y-%m-%d')} to {row['end_date'].strftime('%Y-%m-%d')}")
                lines.append(f"  Drawdown: {row['drawdown']:.2%}")
                lines.append(f"  Peak: ${row['peak']:.2f} -> Trough: ${row['trough']:.2f}")
        
        # Add news correlation if available
        if self.news_api_key:
            lines.append("\n" + "-" * 60)
            lines.append("NEWS CORRELATION (Top 3 Drawdowns)")
            lines.append("-" * 60)
            
            correlation = self.correlate_events(equity_curve, query)
            
            for i, item in enumerate(correlation['news_by_period'][:3]):
                period = item['period']
                news = item['news']
                
                lines.append(f"\nDrawdown {i+1}: {period['drawdown']:.2%}")
                lines.append(f"Date Range: {period['start'].strftime('%Y-%m-%d')} to {period['end'].strftime('%Y-%m-%d')}")
                
                if not news.empty:
                    lines.append("  Top Headlines:")
                    for _, article in news.head(3).iterrows():
                        title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
                        lines.append(f"    - {title}")
                else:
                    lines.append("  No news found")
        
        return "\n".join(lines)


# Convenience function
def analyze_drawdowns(equity_curve: pd.Series, 
                     news_api_key: str = None,
                     query: str = "stock market") -> Dict:
    """
    Quick function to analyze drawdowns.
    
    Args:
        equity_curve: Portfolio value series
        news_api_key: NewsAPI key
        query: News search query
        
    Returns:
        Analysis results dictionary
    """
    analyzer = DrawdownAnalyzer(news_api_key)
    return analyzer.correlate_events(equity_curve, query)


__all__ = ['DrawdownAnalyzer', 'analyze_drawdowns']
