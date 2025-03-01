import os
import pandas as pd
import yfinance as yf
import datetime
import time
from tqdm import tqdm

def get_sp500_top_50():
    """
    Get the list of S&P 500 top 50 companies by market cap
    """
    # Using the S&P 500 components data and sorting by market cap
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

    # Get real-time market caps using yfinance
    market_caps = {}
    print("Fetching market cap data for S&P 500 components...")
    for ticker in tqdm(sp500['Symbol'].tolist()):
        try:
            ticker_yf = yf.Ticker(ticker.replace('.', '-'))
            market_cap = ticker_yf.info.get('marketCap', 0)
            market_caps[ticker] = market_cap
            time.sleep(0.2)  # Adding delay to avoid rate limiting
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            market_caps[ticker] = 0

    # Add market cap to DataFrame and sort
    sp500['MarketCap'] = sp500['Symbol'].map(market_caps)
    top_50 = sp500.sort_values('MarketCap', ascending=False).head(50)

    return top_50['Symbol'].tolist()

def download_granular_data(tickers, start_date, end_date, interval, output_dir):
    """
    Download granular price data for a list of tickers

    Parameters:
    - tickers: List of stock tickers
    - start_date: Start date for historical data
    - end_date: End date for historical data
    - interval: Data granularity (e.g., "1h" for hourly, "1m" for minute)
    - output_dir: Directory to save the data
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Yahoo Finance API limitations for historical data:
    # - 1m: last 7 days only
    # - 2m, 5m, 15m, 30m: last 60 days only
    # - 1h: last 730 days (2 years) only
    # - 1d and above: full historical data

    # Calculate actual available start date based on interval limitations
    today = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    requested_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    interval_limits = {
        "1m": 7,
        "2m": 60,
        "5m": 60,
        "15m": 60,
        "30m": 60,
        "1h": 700,
        "1d": float('inf'),
        "5d": float('inf'),
        "1wk": float('inf'),
        "1mo": float('inf'),
        "3mo": float('inf')
    }

    max_days = interval_limits.get(interval, float('inf'))
    earliest_possible_date = today - datetime.timedelta(days=max_days)
    actual_start = max(requested_start, earliest_possible_date)

    if actual_start > requested_start:
        print(f"Note: {interval} data is only available for the last {max_days} days.")
        print(f"Using {actual_start.strftime('%Y-%m-%d')} instead of requested {start_date}")

    # Download data for each ticker
    print(f"Downloading {interval} data for {len(tickers)} stocks...")
    for ticker in tqdm(tickers):
        try:
            # Replace dots with hyphens for tickers like BRK.B -> BRK-B
            ticker_yf = ticker.replace('.', '-')

            # File to save the data
            output_file = os.path.join(output_dir, f"{ticker}_{interval}_prices.csv")

            # For intervals with limitations, download directly
            data = yf.download(
                ticker_yf,
                start=actual_start.strftime("%Y-%m-%d"),
                end=end_date,
                interval=interval,
                auto_adjust=True,
                progress=False
            )

            # Save to CSV
            if not data.empty:
                data.to_csv(output_file)
                print(f"Successfully downloaded {data.shape[0]} {interval} records for {ticker}")
            else:
                print(f"No {interval} data available for {ticker}")

            # Add delay to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"Error downloading {interval} data for {ticker}: {e}")

def download_optimal_data(tickers, start_date, end_date, granularities, output_dir):
    """
    Download optimal data for different time ranges at maximum available granularity

    Parameters:
    - tickers: List of stock tickers
    - start_date: Overall start date for historical data
    - end_date: End date for historical data
    - granularities: List of granularities to download (e.g., ["1m", "1h", "1d"])
    - output_dir: Directory to save the data
    """
    today = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    for interval in granularities:
        # Determine the appropriate date range for each granularity
        if interval == "1m":
            # 1-minute data: last 7 days only
            interval_start = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            print(f"\nDownloading 1-minute data for the last 7 days ({interval_start} to {end_date})...")
            download_granular_data(tickers, interval_start, end_date, interval, output_dir)

        elif interval in ["2m", "5m", "15m", "30m"]:
            # Intraday data: last 60 days only
            interval_start = (today - datetime.timedelta(days=60)).strftime("%Y-%m-%d")
            print(f"\nDownloading {interval} data for the last 60 days ({interval_start} to {end_date})...")
            download_granular_data(tickers, interval_start, end_date, interval, output_dir)

        elif interval == "1h":
            # Hourly data: last 730 days (2 years) only
            interval_start = (today - datetime.timedelta(days=730)).strftime("%Y-%m-%d")
            requested_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            actual_start = max(requested_start, today - datetime.timedelta(days=730))
            print(f"\nDownloading hourly data for up to 2 years ({actual_start.strftime('%Y-%m-%d')} to {end_date})...")
            download_granular_data(tickers, actual_start.strftime("%Y-%m-%d"), end_date, interval, output_dir)

        else:
            # Daily data or longer: full historical range
            print(f"\nDownloading {interval} data for the full requested range ({start_date} to {end_date})...")
            download_granular_data(tickers, start_date, end_date, interval, output_dir)

def main(granularities=None):
    """
    Main function to download historical price data

    Parameters:
    - granularities: List of granularities to download. If None, downloads all available.
      Options include: "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
    """
    # Set date range
    start_date = "2018-01-01"
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Set output directory
    output_dir = "../data"
    os.makedirs(output_dir, exist_ok=True)

    # Get top 50 S&P 500 companies by market cap
    print("Getting top 50 S&P 500 companies by market cap...")

    top_50_tickers = []
    file_path = os.path.join(output_dir, "top_50_tickers.txt")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            top_50_tickers = f.read().splitlines()
    else:
        top_50_tickers = get_sp500_top_50()  # Assuming this function is defined elsewhere
        # Write the list of top 50 tickers to a file
        with open(file_path, "w") as f:
            f.write("\n".join(top_50_tickers))


    # If no granularities specified, use a default set
    if granularities is None:
        granularities = ["1m", "5m", "1h", "1d"]

    # Download data at specified granularities
    download_optimal_data(top_50_tickers, start_date, end_date, granularities, output_dir)

    print("Download complete!")

if __name__ == "__main__":
    # You can customize the granularities by passing a list to main()
    # e.g., main(["1m", "5m", "1h", "1d"])
    main(["1h"])