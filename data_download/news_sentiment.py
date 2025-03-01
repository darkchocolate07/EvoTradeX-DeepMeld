import os
import time
import requests
import pandas as pd
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Download required NLTK data
nltk.download('vader_lexicon')

# Initialize NLTK's VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Get API key from environment variables
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
if not API_KEY:
    raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables")


def load_tickers(file_path):
    """Load tickers from file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def get_news(ticker):
    """Fetch news for a given ticker."""
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get('feed', [])
    return []


def analyze_sentiment(news_items):
    """Analyze sentiment of news items."""
    if not news_items:
        return 0

    sentiments = []
    for item in news_items:
        title = item.get('title', '')
        summary = item.get('summary', '')
        text = f"{title} {summary}"
        sentiment = sia.polarity_scores(text)
        sentiments.append(sentiment['compound'])

    return sum(sentiments) / len(sentiments) if sentiments else 0


def main():
    # Create output directory if it doesn't exist
    output_dir = "../data/sentiment"
    os.makedirs(output_dir, exist_ok=True)

    # Load tickers
    tickers = load_tickers("../data/top_50_tickers.txt")

    # Initialize results list
    results = []

    # Process each ticker
    for ticker in tickers:
        print(f"Processing {ticker}...")

        try:
            # Get news
            news = get_news(ticker)

            # Analyze sentiment
            sentiment_score = analyze_sentiment(news)

            # Add to results
            results.append({
                'ticker': ticker,
                'sentiment_score': sentiment_score,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")

        # Sleep to respect API rate limits (5 calls per minute for free tier)
        time.sleep(12)

    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    output_file = os.path.join(output_dir, f"sentiment_{datetime.now().strftime('%Y%m%d')}.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()