import os
import pandas as pd


def clean_csv_files(directory="../data"):
    # Walk through all subdirectories in the data directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    # Read the CSV file
                    df = pd.read_csv(file_path)

                    # Keep only the header (1st row) and data (4th row onwards)
                    df = df.iloc[2:]

                    # Save the modified CSV back to the same file
                    df.to_csv(file_path, index=False)
                    print(f"Successfully processed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")


if __name__ == "__main__":
    clean_csv_files()
