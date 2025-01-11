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
output_dir = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\precipitation-curves"
os.makedirs(output_dir, exist_ok=True)

# Define time period groups
period_groups = {
  #  "1-Month": [["January"], ["February"], ["March"], ["April"], ["May"], ["June"],
 #               ["July"], ["August"], ["September"], ["October"], ["November"], ["December"]],
   # "3-Month": [["January", "February", "March"], ["April", "May", "June"],
 #               ["July", "August", "September"], ["October", "November", "December"]],
   # "6-Month": [["January", "February", "March", "April", "May", "June"],
  #              ["July", "August", "September", "October", "November", "December"]],
   # "10-Month": [["September", "October", "November", "December", "January",
    #              "February", "March", "April", "May", "June"]],
    "12-Month": [["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]],
}

# Group precipitation by periods
def group_precipitation(data, groups, group_name):
    results = []
    for group in groups:
        grouped_data = data[data["Month"].isin(group)].groupby("Year")["Precipitation"].sum().reset_index()
        grouped_data.rename(columns={"Precipitation": group_name}, inplace=True)
        results.append(grouped_data)
    return pd.concat(results, keys=range(len(groups)), names=["Group", "Index"]).reset_index()

# Process all period groups
period_data = {}
for period_name, groups in period_groups.items():
    period_data[period_name] = group_precipitation(monthly_data, groups, f"{period_name} Total")

# Probability distribution plotting for Normal, Log-Normal, and Gumbel
def plot_distribution(period, sorted_data, probabilities, x_fit, cdf_fit, method_name, color, file_suffix):
    # Create the plot
    fig = go.Figure()

    # Raw precipitation data
    fig.add_trace(go.Scatter(
        x=probabilities,
        y=sorted_data,
        mode='markers',
        name='Raw Precipitation',
        marker=dict(color='blue'),
        text=[f'Probability: {prob:.2f}%, Precipitation: {val:.2f}' for prob, val in zip(probabilities, sorted_data)],
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

    # Layout adjustments
    fig.update_layout(
        title=f"{method_name} Distribution for {period}",
        xaxis_title="Probability (%)",
        yaxis_title="Precipitation (kg/m²)",
        template="plotly_white"
    )

    # Save plot as HTML
    file_name = os.path.join(output_dir, f"{method_name}_Probability_{file_suffix}_{period}.html")
    fig.write_html(file_name)

# Generate plots for each period
for period_name, data in period_data.items():
    for group in data["Group"].unique():
        group_data = data[data["Group"] == group][f"{period_name} Total"].dropna()

        if len(group_data) > 0:
            # Sort data
            sorted_data = np.sort(group_data)
            probabilities = 100 * (np.arange(1, len(sorted_data) + 1) / (len(sorted_data) + 1))

            # Log-Normal Distribution
            shape, loc, scale = lognorm.fit(sorted_data, floc=0)
            x_fit = np.linspace(sorted_data.min(), sorted_data.max(), 100)
            cdf_fit = lognorm.cdf(x_fit, shape, loc, scale)
            plot_distribution(f"{period_name} Group {group}", sorted_data, probabilities, x_fit, cdf_fit, "Log-Normal", "red", "lognormal")

            # Normal Distribution
            mean, std = norm.fit(sorted_data)
            cdf_fit = norm.cdf(x_fit, mean, std)
            plot_distribution(f"{period_name} Group {group}", sorted_data, probabilities, x_fit, cdf_fit, "Normal", "green", "normal")

            # Gumbel Distribution
            loc, scale = gumbel_r.fit(sorted_data)
            cdf_fit = gumbel_r.cdf(x_fit, loc, scale)
            plot_distribution(f"{period_name} Group {group}", sorted_data, probabilities, x_fit, cdf_fit, "Gumbel", "purple", "gumbel")

print("Probability vs Precipitation plots for Log-Normal, Normal, and Gumbel distributions by periods have been generated and saved.")
