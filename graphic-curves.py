import pandas as pd
import numpy as np
from scipy.stats import lognorm, norm, gumbel_r
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
output_dir = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\probability-curves"
os.makedirs(output_dir, exist_ok=True)

# Probability distribution plotting for Normal, Log-Normal, and Gumbel
months = monthly_data["Month"].unique()

def plot_distribution(month, sorted_data, probabilities, x_fit, cdf_fit, method_name, color, file_suffix):
    # Create the plot
    fig = go.Figure()

    # Raw rainfall data
    fig.add_trace(go.Scatter(
        x=probabilities,
        y=sorted_data,
        mode='markers',
        name='Raw Rainfall',
        marker=dict(color='blue'),
        text=[f'Probability: {prob:.2f}%, Rainfall: {val:.2f} kg/m²' for prob, val in zip(probabilities, sorted_data)],
        hoverinfo='text'
    ))

    # Fit line
    fig.add_trace(go.Scatter(
        x=cdf_fit * 100,
        y=x_fit,
        mode='lines',
        name=f'{method_name} Fit',
        line=dict(color=color)
    ))

    # Layout adjustments for probability vs Qp
    fig.update_layout(
        title=f"{method_name} Distribution and Raw Rainfall for {month}",
        xaxis_title="Probability (%)",
        yaxis_title="Rainfall (kg/m²)",
        template="plotly_white",
        xaxis=dict(type= 'log' , title="Probability (%)"),
        yaxis=dict( type= 'log', title="Rainfall (kg/m²)")
    )

    # Save plot as HTML
    file_name = os.path.join(output_dir, f"{method_name}_Probability_{file_suffix}_{month}.html")
    fig.write_html(file_name)

for month in months:
    month_data = monthly_data[monthly_data["Month"] == month]["Precipitation"].dropna()
    
    if len(month_data) > 0:
        # Sort data
        sorted_data = np.sort(month_data)
        probabilities = 100 * (np.arange(1, len(sorted_data) + 1) / (len(sorted_data) + 1))

        # Log-Normal Distribution
        shape, loc, scale = lognorm.fit(sorted_data, floc=0)
        x_fit = np.linspace(sorted_data.min(), sorted_data.max(), 100)
        cdf_fit = lognorm.cdf(x_fit, shape, loc, scale)
        plot_distribution(month, sorted_data, probabilities, x_fit, cdf_fit, "Log-Normal", "red", "lognormal")

        # Normal Distribution
        mean, std = norm.fit(sorted_data)
        cdf_fit = norm.cdf(x_fit, mean, std)
        plot_distribution(month, sorted_data, probabilities, x_fit, cdf_fit, "Normal", "green", "normal")

        # Gumbel Distribution
        loc, scale = gumbel_r.fit(sorted_data)
        cdf_fit = gumbel_r.cdf(x_fit, loc, scale)
        plot_distribution(month, sorted_data, probabilities, x_fit, cdf_fit, "Gumbel", "purple", "gumbel")

print("Probability vs Rainfall plots for Log-Normal, Normal, and Gumbel distributions have been generated and saved.")
