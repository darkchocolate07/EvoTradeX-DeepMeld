import pandas as pd
import numpy as np


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) for a given price series.

    Args:
        data: Price series (typically closing prices)
        period: RSI calculation period (default: 14)

    Returns:
        RSI values as a pandas Series
    """
    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))

    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(data: pd.Series,
                   fast_period: int = 12,
                   slow_period: int = 26,
                   signal_period: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate the Moving Average Convergence Divergence (MACD).

    Args:
        data: Price series (typically closing prices)
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)

    Returns:
        Tuple of (MACD line, Signal line, MACD histogram)
    """
    # Calculate EMAs
    ema_fast = data.ewm(span=fast_period, adjust=False).mean()
    ema_slow = data.ewm(span=slow_period, adjust=False).mean()

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate Signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Calculate MACD histogram
    macd_histogram = macd_line - signal_line

    return macd_line, signal_line, macd_histogram


def calculate_bollinger_bands(data: pd.Series,
                              period: int = 20,
                              num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.

    Args:
        data: Price series (typically closing prices)
        period: Moving average period (default: 20)
        num_std: Number of standard deviations for bands (default: 2.0)

    Returns:
        Tuple of (Upper Band, Middle Band, Lower Band)
    """
    # Calculate middle band (simple moving average)
    middle_band = data.rolling(window=period).mean()

    # Calculate standard deviation
    std = data.rolling(window=period).std()

    # Calculate upper and lower bands
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)

    return upper_band, middle_band, lower_band


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to a price DataFrame.

    Args:
        df: DataFrame with at least 'Close' price column

    Returns:
        DataFrame with added technical indicators
    """
    # Ensure we have the required column
    if 'Close' not in df.columns:
        raise ValueError("DataFrame must contain 'Close' price column")

    # Calculate RSI
    df['RSI'] = calculate_rsi(df['Close'])

    # Calculate MACD
    macd_line, signal_line, macd_hist = calculate_macd(df['Close'])
    df['MACD'] = macd_line
    df['MACD_Signal'] = signal_line
    df['MACD_Histogram'] = macd_hist

    # Calculate Bollinger Bands
    upper_band, middle_band, lower_band = calculate_bollinger_bands(df['Close'])
    df['BB_Upper'] = upper_band
    df['BB_Middle'] = middle_band
    df['BB_Lower'] = lower_band

    return df


if __name__ == "__main__":
    # Example usage
    try:
        # Load sample data
        sample_data = pd.read_csv("../data/AAPL.csv")

        # Add technical indicators
        sample_data = add_technical_indicators(sample_data)

        print("Technical indicators calculated successfully")
        print(sample_data.tail())
    except Exception as e:
        print(f"Error calculating indicators: {str(e)}")