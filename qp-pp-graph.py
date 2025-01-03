import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Load the data
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Directory where the graphs will be saved
graphs_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs\qp-pp"
os.makedirs(graphs_path, exist_ok=True)

# Columns represent months (excluding the first column which is Year)
months = data.columns[1:]

# Probability calculation function: 100 * m / (n + 1)
def calculate_probabilities(precipitation):
    n = len(precipitation)
    sorted_precipitation = np.sort(precipitation)
    return 100 * (np.arange(1, n + 1) / (n + 1))

# Creating graphs for each month
for month in months:
    monthly_data = data[["Year", month]].dropna()  # Remove NaN values
    sorted_data = monthly_data.sort_values(by=month)
    precipitation = sorted_data[month].values  # Precipitation data (Qp)
    years = sorted_data["Year"].values

    # Calculate probabilities
    probabilities = calculate_probabilities(precipitation)

    # Create the graph
    fig = go.Figure()

    # Rainfall (Qp) vs Probability (PP) plot
    fig.add_trace(go.Scatter(x=probabilities, y=precipitation, mode='markers+lines', name=month,
                             marker=dict(color='blue'),
                             text=[f'Year: {y}<br>Qp: {v:.2f}<br>Probability: {p:.2f}' for y, p, v in zip(years, probabilities, precipitation)],
                             hoverinfo='text'))

    # Layout adjustments
    fig.update_layout(
        title=f'{month} Month - Rainfall vs Probability',
        xaxis_title='Probability (%) (Log Scale)',
        yaxis_title='Qp (kg/m²)',
        xaxis_type='log',  # Logarithmic scale for the X-axis
        template='plotly_dark'
    )
    
    # Save the graph
    file_path = os.path.join(graphs_path, f"{month}_rainfall_probability_plot.html")
    fig.write_html(file_path)

print("Graphs have been successfully saved.")
