import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go

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
    bins = np.linspace(monthly_data.min(), monthly_data.max(), 20)

    # If all values are the same, skip creating the histogram
    if monthly_data.min() == monthly_data.max():
        print(f"Warning: Data for {month} contains a single constant value.")
        continue

    # Compute histogram and frequencies
    n, bins = np.histogram(monthly_data, bins=bins)
    relative_freq = n / n.sum()  # Relative frequency
    cumulative_freq = np.cumsum(n)  # Cumulative frequency
    cumulative_relative_freq = cumulative_freq / n.sum()  # Normalized cumulative frequency

    # Create frequency table
    frequency_table = pd.DataFrame({
        'Bin Start': bins[:-1],
        'Bin End': bins[1:],
        'Frequency (Ni)': n,
        'Relative Frequency (Ni/n)': relative_freq,
        'Cumulative Frequency': cumulative_freq,
        'Relative Cumulative Frequency (F/n)': cumulative_relative_freq
    })

    # Save the frequency table
    table_file_path = os.path.join(tables_path, f"{month}_frequency_table.csv")
    frequency_table.to_csv(table_file_path, index=False)

    # Create the plotly graph
    fig = go.Figure()

    # Add histogram (frequency)
    fig.add_trace(go.Bar(
        x=(bins[:-1] + bins[1:]) / 2,  # Bin centers
        y=relative_freq,
        width=(bins[1] - bins[0]) * 0.8,  # Adjust bar width
        marker_color='blue',
        name='Frequency (Relative)',
        opacity=0.7
    ))

    # Add cumulative frequency (step plot)
    fig.add_trace(go.Scatter(
        x=np.repeat(bins, 2)[1:-1],  # Step-like x values
        y=np.repeat(cumulative_relative_freq, 2),  # Step-like y values
        mode='lines',
        line=dict(color='red', width=2),
        name='Cumulative Frequency (Step)'
    ))

    # Update layout
    fig.update_layout(
        title=f'Frequency and Cumulative Frequency Distribution ({month})',
        xaxis=dict(title='Precipitation Amount (m³/s)', tickmode='linear'),
        yaxis=dict(title='Frequency / Cumulative Frequency'),
        legend=dict(title='Legend', x=0.8, y=1),
        template='plotly_white'
    )

    # Save the graph as an HTML file
    file_path = os.path.join(graphs_path, f"{month}_frequency_and_cumulative_distribution.html")
    fig.write_html(file_path)

    print(f"Processing for {month} completed. Graph saved to {file_path}.")

print("All processes are completed!")
