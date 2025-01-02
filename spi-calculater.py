import pandas as pd
import numpy as np

def calculate_spi(data, fill_method='mean'):
    """
    Calculates the Standardized Precipitation Index (SPI) for a given precipitation data series.

    Args:
        data (pd.Series): The precipitation data series.
        fill_method (str, optional): The method to use for filling missing values (NaN). Defaults to 'mean'.

    Returns:
        pd.Series: The SPI values for the data series.
    """

    # Fill NaN values using the mean
    if fill_method == 'mean':
        data = data.fillna(data.mean())
    else:
        raise ValueError("Invalid fill method")

    # Calculate mean and standard deviation
    mean = np.mean(data)
    std = np.std(data)

    # Handle zero standard deviation to avoid division by zero error
    if std == 0:
        std = 1e-8

    # Calculate SPI using the standardized anomaly (data - mean) / standard deviation
    spi = (data - mean) / std
    return spi

def calculate_spi_for_period(rainfall_data, window, fill_method='mean'):
    """
    Calculates SPI for rolling window periods across the precipitation data.

    Args:
        rainfall_data (pd.DataFrame): The precipitation data DataFrame.
        window (int): The window size (number of months) for SPI calculation.
        fill_method (str, optional): The method to use for filling missing values (NaN). Defaults to 'mean'.

    Returns:
        pd.DataFrame: A DataFrame containing SPI values for each window period.
    """

    spi_values = {}
    months = list(rainfall_data.index)

    # Iterate through the data with the window size
    for i in range(0, len(months), window):
        end = min(i + window, len(months))  # Control index for the last window
        group = months[i:end]
        grouped_data = rainfall_data.loc[group].mean()  # Calculate mean for the window
        spi_values[",".join(group)] = calculate_spi(grouped_data, fill_method)

    spi_df = pd.DataFrame(spi_values).T
    spi_df.columns = rainfall_data.columns
    spi_df.index.name = "Month"
    return spi_df

# Read precipitation data from CSV file
df = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Reshape data by transposing (years become columns, months become index)
rainfall_data = df.drop(columns='Year').T
rainfall_data.columns = df['Year']
rainfall_data.index.name = "Month"

# Calculate SPI for different window sizes
windows = [1, 3, 6, 12]
for window in windows:
    spi_df = calculate_spi_for_period(rainfall_data, window, fill_method='mean')
    file_name = f"spi_values_{window}_month_period.xlsx"
    spi_df.to_excel(file_name, index=True)
    print(f"{window}-month period SPI calculation completed and saved to '{file_name}'.")