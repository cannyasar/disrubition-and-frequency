import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Load the CSV file
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Folders where graphs and frequency tables will be saved
graphs_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs\fre-graphs"
tables_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\tables\fre-table"




os.makedirs(graphs_path, exist_ok=True)
os.makedirs(tables_path, exist_ok=True)

# Define the month names (assumes the first column contains year information)
months = data.columns[1:]

# Generate histogram and cumulative frequency graph for each month
for month in months:
    print(f"Processing {month}...")
    monthly_data = data[month].dropna()  # Remove missing data

    if len(monthly_data) == 0:
        print(f"No data available for {month}, skipping.")
        continue

    # Define bins (ranges) for the histogram
    bins = np.linspace(min(monthly_data), max(monthly_data), 20)

    # If all values are the same, skip creating the histogram
    if min(monthly_data) == max(monthly_data):
        print(f"Warning: Data for {month} contains a single constant value.")
        continue

    # Compute the histogram
    n, bins = np.histogram(monthly_data, bins=bins)
    relative_freq = n / len(monthly_data)  # Relative frequency
    cumulative_freq = np.cumsum(n)  # Cumulative frequency
    cumulative_relative_freq = cumulative_freq / len(monthly_data)  # Relative cumulative frequency

    # Check if the sum of relative frequencies equals 1
    if not np.isclose(np.sum(relative_freq), 1):
        print(f"Warning: Relative frequencies for {month} do not sum to 1. Total: {np.sum(relative_freq)}")

    # Check if cumulative frequency is monotonic
    if not all(cumulative_freq[i] <= cumulative_freq[i+1] for i in range(len(cumulative_freq)-1)):
        print(f"Warning: Cumulative frequency for {month} is not monotonic.")

    # Create frequency table
    frequency_table = pd.DataFrame({
        'Bin Start': bins[:-1],
        'Bin End': bins[1:],
        'Frequency (Ni)': n,
        'Relative Frequency (Ni/n)': relative_freq,
        'Cumulative Frequency (F)': cumulative_freq,
        'Relative Cumulative Frequency (F/n)': cumulative_relative_freq
    })

    # Save the frequency table
    table_file_path = os.path.join(tables_path, f"{month}_frequency_table.csv")
    frequency_table.to_csv(table_file_path, index=False)

    # Create the graph
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Bar width is adjusted to leave space between bars
    bar_width = (bins[1] - bins[0]) * 0.8

    # Left axis: Relative Frequency Histogram
    ax1.bar((bins[:-1] + bins[1:]) / 2, relative_freq, width=bar_width, color='blue', alpha=0.7, label='Relative Frequency Histogram', edgecolor='black')
    ax1.set_xlabel('Precipitation Amount (m³/s)')
    ax1.set_ylabel(r'$f \left( \frac{N_i}{n} \right)$', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    # Right axis: Cumulative Frequency Distribution
    ax2 = ax1.twinx()  # Create a new axis sharing the same x-axis
    ax2.plot((bins[:-1] + bins[1:]) / 2, cumulative_relative_freq, color='green', marker='o', label='Cumulative Frequency', linewidth=2)
    ax2.set_ylabel(r'$F(X_i)$', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Title and graph adjustments
    plt.title(f'{month} Frequency Histogram and Cumulative Frequency Distribution')
    
    # Adjust legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Save the graph
    file_path = os.path.join(graphs_path, f"{month}_frequency_and_cumulative_distribution_overlay.png")
    plt.tight_layout()  # Better layout
    plt.savefig(file_path, dpi=300)  # Save with high resolution
    plt.close()

    print(f"Processing for {month} completed.")
    
print("All processes are completed!")
