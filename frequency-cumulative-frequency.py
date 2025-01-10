import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# Load the data
file_path = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\data\\precipitation_data.csv"
data = pd.read_csv(file_path)

# Convert monthly data to long format
monthly_data = data.melt(id_vars=["Year"], var_name="Month", value_name="Precipitation")
monthly_data["Month"] = pd.Categorical(
    monthly_data["Month"],
    categories=["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"],
    ordered=True
)
monthly_data.sort_values(by=["Year", "Month"], inplace=True)

# Convert zero or negative values to a positive value
monthly_data["Precipitation"] = monthly_data["Precipitation"].apply(lambda x: x if x > 0 else 0.01)

# Directory to save graphs
output_dir = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\frequency-graphs"
os.makedirs(output_dir, exist_ok=True)

# Transformation and plotting
months = monthly_data["Month"].unique()

for month in months:
    month_data = monthly_data[monthly_data["Month"] == month]["Precipitation"].dropna()
    
    if len(month_data) > 0:
        # Create bins for histogram
        bins = np.linspace(month_data.min(), month_data.max(), num=10)
        hist, bin_edges = np.histogram(month_data, bins=bins, density=False)
        cumulative = np.cumsum(hist) / hist.sum()

        # Create the plot
        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Bar(
            x=bin_edges[:-1],
            y=hist / hist.sum(),  # Normalize to probability
            name='Frequency Histogram',
            marker=dict(color='blue'),
            opacity=0.6
        ))

        # Cumulative frequency (step-like)
        fig.add_trace(go.Scatter(
            x=np.repeat(bin_edges, 2)[1:-1],
            y=np.repeat(cumulative, 2),
            mode='lines',
            name='Cumulative Frequency (Step)',
            line=dict(color='red', dash='solid')
        ))

        # Layout adjustments
        fig.update_layout(
            title=f"Frequency and Cumulative Distribution for {month}",
            xaxis_title="Discharge (m³/s)",
            yaxis_title="Frequency / Cumulative Probability",
            template="plotly_white",
            xaxis=dict(type='linear', tickmode='linear', dtick=100),
            yaxis=dict(tickmode='linear', dtick=0.1)
        )

        # Save plot as HTML
        file_name = os.path.join(output_dir, f"Discharge_Distribution_{month}.html")
        fig.write_html(file_name)

print("Discharge distribution curves with step-like cumulative frequency have been generated and saved.")
