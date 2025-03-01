import os
import requests
import pandas as pd
import datetime
import time
from dotenv import load_dotenv
from tqdm import tqdm
import json

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path='../.env')

class InsiderTradingAnalyzer:
    def __init__(self):
        """Initialize the analyzer with API key from environment variables"""
        self.api_key = os.getenv('QUIVER_API_KEY')
        if not self.api_key:
            raise ValueError("QUIVER_API_KEY not found in .env file")

        self.base_url = "https://api.quiverquant.com/beta"
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        # Create output directory
        self.output_dir = os.path.join('..', 'data', 'insider')
        os.makedirs(self.output_dir, exist_ok=True)

    def get_sp500_tickers(self):
        """Get S&P 500 tickers as a sample of companies to analyze"""
        try:
            sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
            return sp500['Symbol'].tolist()
        except Exception as e:
            print(f"Error fetching S&P 500 tickers: {e}")
            # Return a small subset of major companies as fallback
            return ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "JPM", "V", "JNJ"]

    def fetch_insider_trading(self, ticker):
        """Fetch insider trading data for a specific ticker"""
        endpoint = f"/live/insiders/{ticker}"
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching insider trading for {ticker}: {response.status_code}")
                return []
        except Exception as e:
            print(f"Request error for {ticker} insider trading: {e}")
            return []

    def fetch_sec_filings(self, ticker):
        """Fetch SEC filings for a specific ticker"""
        endpoint = f"/live/forms/{ticker}"
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching SEC filings for {ticker}: {response.status_code}")
                return []
        except Exception as e:
            print(f"Request error for {ticker} SEC filings: {e}")
            return []

    def analyze_insider_sentiment(self, insider_data):
        """
        Analyze insider trading data to determine sentiment

        Returns a dictionary with:
        - buy_count: Number of buy transactions
        - sell_count: Number of sell transactions
        - net_shares: Net shares bought (positive) or sold (negative)
        - net_value: Net value of transactions in USD
        - sentiment: Overall sentiment (Bullish, Bearish, or Neutral)
        """
        if not insider_data:
            return {
                'buy_count': 0,
                'sell_count': 0,
                'net_shares': 0,
                'net_value': 0,
                'sentiment': 'Neutral'
            }

        buy_count = 0
        sell_count = 0
        net_shares = 0
        net_value = 0

        for trade in insider_data:
            transaction_type = trade.get('TransactionType', '').upper()
            shares = trade.get('Shares', 0)
            value = trade.get('Value', 0)

            if 'BUY' in transaction_type or 'PURCHASE' in transaction_type:
                buy_count += 1
                net_shares += shares
                net_value += value
            elif 'SELL' in transaction_type or 'DISPOSITION' in transaction_type:
                sell_count += 1
                net_shares -= shares
                net_value -= value

        # Determine sentiment
        if net_value > 0 and buy_count > sell_count:
            sentiment = 'Bullish'
        elif net_value < 0 and sell_count > buy_count:
            sentiment = 'Bearish'
        else:
            sentiment = 'Neutral'

        return {
            'buy_count': buy_count,
            'sell_count': sell_count,
            'net_shares': net_shares,
            'net_value': net_value,
            'sentiment': sentiment
        }

    def analyze_sec_filings(self, filings_data):
        """
        Analyze SEC filings to determine institutional activity

        Returns a dictionary with:
        - form_counts: Count of each form type
        - recent_filing_count: Number of filings in the last 90 days
        - key_filings: List of significant filings (13F, 13G, 13D)
        """
        if not filings_data:
            return {
                'form_counts': {},
                'recent_filing_count': 0,
                'key_filings': []
            }

        form_counts = {}
        key_filings = []
        recent_filing_count = 0

        ninety_days_ago = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%d')

        for filing in filings_data:
            form_type = filing.get('FormType', '')
            date = filing.get('Date', '')

            # Count form types
            if form_type in form_counts:
                form_counts[form_type] += 1
            else:
                form_counts[form_type] = 1

            # Check for recent filings
            if date >= ninety_days_ago:
                recent_filing_count += 1

            # Track key filings that indicate institutional interest
            if form_type in ['13F', '13G', '13D', '13F-HR']:
                key_filings.append({
                    'form_type': form_type,
                    'date': date,
                    'filer': filing.get('Filer', ''),
                    'description': filing.get('Description', '')
                })

        return {
            'form_counts': form_counts,
            'recent_filing_count': recent_filing_count,
            'key_filings': key_filings
        }

    def calculate_institutional_confidence(self, insider_sentiment, sec_analysis):
        """
        Calculate an institutional confidence score based on insider trading and SEC filings

        Returns a score between -100 (very bearish) and 100 (very bullish)
        """
        # Base score from insider sentiment
        if insider_sentiment['sentiment'] == 'Bullish':
            base_score = 50
        elif insider_sentiment['sentiment'] == 'Bearish':
            base_score = -50
        else:
            base_score = 0

        # Adjust based on insider trading metrics
        buy_sell_ratio = 0
        if insider_sentiment['sell_count'] > 0:
            buy_sell_ratio = insider_sentiment['buy_count'] / insider_sentiment['sell_count']
        elif insider_sentiment['buy_count'] > 0:
            buy_sell_ratio = 2  # Arbitrary positive value when there are buys but no sells

        if buy_sell_ratio > 1:
            base_score += min(25, (buy_sell_ratio - 1) * 10)
        elif buy_sell_ratio > 0:
            base_score -= min(25, (1 - buy_sell_ratio) * 10)

        # Adjust based on SEC filings
        # More 13F/13G filings indicate institutional interest
        key_filing_count = len(sec_analysis['key_filings'])
        if key_filing_count > 5:
            base_score += 15
        elif key_filing_count > 2:
            base_score += 10
        elif key_filing_count > 0:
            base_score += 5

        # Clip the final score to -100 to 100 range
        return max(-100, min(100, base_score))

    def process_company(self, ticker):
        """Process insider trading and SEC filings for a specific company"""
        print(f"Processing {ticker}...")

        # Fetch data
        insider_data = self.fetch_insider_trading(ticker)
        filings_data = self.fetch_sec_filings(ticker)

        # Analyze data
        insider_sentiment = self.analyze_insider_sentiment(insider_data)
        sec_analysis = self.analyze_sec_filings(filings_data)

        # Calculate confidence score
        confidence_score = self.calculate_institutional_confidence(insider_sentiment, sec_analysis)

        # Prepare result
        result = {
            'ticker': ticker,
            'analysis_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'insider_trading': {
                'data': insider_data,
                'analysis': insider_sentiment
            },
            'sec_filings': {
                'data': filings_data,
                'analysis': sec_analysis
            },
            'institutional_confidence_score': confidence_score,
            'confidence_category': self.get_confidence_category(confidence_score)
        }

        # Save result
        self.save_result(ticker, result)

        return result

    def get_confidence_category(self, score):
        """Convert numerical score to confidence category"""
        if score >= 75:
            return "Very Bullish"
        elif score >= 25:
            return "Bullish"
        elif score > -25:
            return "Neutral"
        elif score > -75:
            return "Bearish"
        else:
            return "Very Bearish"

    def save_result(self, ticker, result):
        """Save analysis result to file"""
        file_path = os.path.join(self.output_dir, f"{ticker}_insider_analysis.json")
        with open(file_path, 'w') as f:
            json.dump(result, f, indent=2)

        # Also save a summary CSV
        summary = {
            'Ticker': ticker,
            'Analysis Date': result['analysis_date'],
            'Confidence Score': result['institutional_confidence_score'],
            'Confidence Category': result['confidence_category'],
            'Insider Buy Count': result['insider_trading']['analysis']['buy_count'],
            'Insider Sell Count': result['insider_trading']['analysis']['sell_count'],
            'Net Shares': result['insider_trading']['analysis']['net_shares'],
            'Net Value ($)': result['insider_trading']['analysis']['net_value'],
            'Insider Sentiment': result['insider_trading']['analysis']['sentiment'],
            'Recent SEC Filings': result['sec_filings']['analysis']['recent_filing_count'],
            'Key Institutional Filings': len(result['sec_filings']['analysis']['key_filings'])
        }

        summary_df = pd.DataFrame([summary])
        summary_path = os.path.join(self.output_dir, f"{ticker}_summary.csv")
        summary_df.to_csv(summary_path, index=False)

    def generate_aggregate_report(self, results):
        """Generate an aggregate report of all analyzed companies"""
        if not results:
            return

        # Create aggregate summary DataFrame
        summary_rows = []
        for ticker, result in results.items():
            summary_rows.append({
                'Ticker': ticker,
                'Analysis Date': result['analysis_date'],
                'Confidence Score': result['institutional_confidence_score'],
                'Confidence Category': result['confidence_category'],
                'Insider Buy Count': result['insider_trading']['analysis']['buy_count'],
                'Insider Sell Count': result['insider_trading']['analysis']['sell_count'],
                'Net Shares': result['insider_trading']['analysis']['net_shares'],
                'Net Value ($)': result['insider_trading']['analysis']['net_value'],
                'Insider Sentiment': result['insider_trading']['analysis']['sentiment'],
                'Recent SEC Filings': result['sec_filings']['analysis']['recent_filing_count'],
                'Key Institutional Filings': len(result['sec_filings']['analysis']['key_filings'])
            })

        summary_df = pd.DataFrame(summary_rows)
        summary_df.sort_values('Confidence Score', ascending=False, inplace=True)

        # Save aggregate report
        report_path = os.path.join(self.output_dir, "aggregate_insider_analysis.csv")
        summary_df.to_csv(report_path, index=False)

        # Also save distribution of confidence categories
        category_counts = summary_df['Confidence Category'].value_counts().reset_index()
        category_counts.columns = ['Confidence Category', 'Count']
        category_path = os.path.join(self.output_dir, "confidence_distribution.csv")
        category_counts.to_csv(category_path, index=False)

def main():
    analyzer = InsiderTradingAnalyzer()

    # Get tickers (using S&P 500 as an example)
    tickers = analyzer.get_sp500_tickers()
    print(f"Retrieved {len(tickers)} tickers for analysis")

    # Analyze each company (limit to first 50 for demo purposes)
    results = {}
    for ticker in tqdm(tickers[:50]):
        try:
            results[ticker] = analyzer.process_company(ticker)
            # Add delay to avoid API rate limits
            time.sleep(1)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # Generate aggregate report
    analyzer.generate_aggregate_report(results)
    print(f"Analysis complete. Results saved to {analyzer.output_dir}")

if __name__ == "__main__":
    main()