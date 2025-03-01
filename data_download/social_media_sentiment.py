import os
import time
import pandas as pd
from datetime import datetime, timedelta
import tweepy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Download required NLTK data
nltk.download('vader_lexicon')

# Initialize NLTK's VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Get Twitter API credentials from environment variables
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
if not TWITTER_BEARER_TOKEN:
    raise ValueError("TWITTER_BEARER_TOKEN not found in environment variables")

# Initialize Twitter client
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)


def load_tickers(file_path):
    """Load tickers from file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def get_social_posts(ticker):
    """Fetch recent tweets about a ticker."""
    # Get tweets from the last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)

    query = f"${ticker} lang:en -is:retweet"  # Search for cashtag, English tweets, no retweets

    try:
        tweets = client.search_recent_tweets(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=100,  # Maximum allowed for basic API access
            tweet_fields=['created_at', 'public_metrics']
        )

        return tweets.data if tweets.data else []
    except Exception as e:
        print(f"Error fetching tweets for {ticker}: {str(e)}")
        return []


def analyze_sentiment(tweets):
    """Analyze sentiment of tweets."""
    if not tweets:
        return 0, 0

    sentiments = []
    total_engagement = 0

    for tweet in tweets:
        # Calculate engagement (likes + retweets)
        engagement = tweet.public_metrics['like_count'] + tweet.public_metrics['retweet_count']
        total_engagement += engagement

        # Calculate sentiment
        sentiment = sia.polarity_scores(tweet.text)
        # Weight the sentiment by engagement
        sentiments.append((sentiment['compound'], engagement))

    if not sentiments:
        return 0, 0

    # Calculate weighted average sentiment
    weighted_sentiment = sum(score * weight for score, weight in sentiments)
    if total_engagement > 0:
        weighted_sentiment /= total_engagement
    else:
        weighted_sentiment = sum(score for score, _ in sentiments) / len(sentiments)

    return weighted_sentiment, total_engagement


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
            # Get social media posts
            tweets = get_social_posts(ticker)

            # Analyze sentiment
            sentiment_score, engagement = analyze_sentiment(tweets)

            # Add to results
            results.append({
                'ticker': ticker,
                'sentiment_score': sentiment_score,
                'engagement': engagement,
                'tweet_count': len(tweets) if tweets else 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")

        # Sleep to respect API rate limits
        time.sleep(1)

    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    output_file = os.path.join(output_dir, f"social_sentiment_{datetime.now().strftime('%Y%m%d')}.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()