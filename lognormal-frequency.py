import pandas as pd
import numpy as np
from scipy.stats import lognorm
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
output_dir = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\lognormal_pdf"
os.makedirs(output_dir, exist_ok=True)

# Transformation and plotting
months = monthly_data["Month"].unique()

for month in months:
    month_data = monthly_data[monthly_data["Month"] == month]["Precipitation"].dropna()

    if len(month_data) > 0:
        # Sort data
        sorted_data = np.sort(month_data)

        # Fit log-normal distribution
        shape, loc, scale = lognorm.fit(sorted_data)  # Removed floc=0
        probabilities = np.linspace(1e-6, 1 - 1e-6, 1000)  # Avoid exact 0 or 1
        x_fit = lognorm.ppf(probabilities, shape, loc, scale)
        y_fit = lognorm.pdf(x_fit, shape, loc, scale)

        # Print fit parameters and sample values for debugging
        print(f"Month: {month}")
        print(f"Shape: {shape}, Loc: {loc}, Scale: {scale}")
        print(f"Sample x_fit: {x_fit[:5]}")
        print(f"Sample y_fit: {y_fit[:5]}")

        # Create the plot
        fig = go.Figure()

        # Log-normal PDF line
        fig.add_trace(go.Scatter(
            x=probabilities * 100,  # Convert probabilities to percentage
            y=y_fit,
            mode="lines",
            name="Log-Normal PDF",
            line=dict(color="green", dash="solid")
        ))

        # Layout adjustments
        fig.update_layout(
            title=f"Log-Normal PDF for {month}",
            xaxis_title="Probability (%)",
            yaxis_title="Probability Density",
            template="plotly_white",
            xaxis=dict(type="linear", tickmode="linear"),
            yaxis=dict(tickmode="linear")
        )

        # Save the plot as an HTML file
        output_file = os.path.join(output_dir, f"lognormal_pdf_{month}.html")
        fig.write_html(output_file)

        print(f"Log-normal PDF plot for {month} saved to: {output_file}")