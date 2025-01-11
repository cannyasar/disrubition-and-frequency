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

# Define month groups
def group_precipitation(data, groups, group_name):
    results = []
    for group in groups:
        grouped_data = data[data["Month"].isin(group)].groupby("Year")["Precipitation"].sum().reset_index()
        grouped_data.rename(columns={"Precipitation": group_name}, inplace=True)
        results.append(grouped_data)
    return results

# Define period groups
one_month_groups = [["January"], ["February"], ["March"], ["April"], ["May"], ["June"], ["July"], ["August"], ["September"], ["October"], ["November"], ["December"]]
three_month_groups = [["January", "February", "March"], ["April", "May", "June"], ["July", "August", "September"], ["October", "November", "December"]]
six_month_groups = [["January", "February", "March", "April", "May", "June"], ["July", "August", "September", "October", "November", "December"]]
ten_month_group = [["September", "October", "November", "December", "January", "February", "March", "April", "May", "June"]]
twelve_month_group = [["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]]

# Calculate total precipitation for each period
one_month_totals = group_precipitation(monthly_data, one_month_groups, "1-Month Total")
three_month_totals = group_precipitation(monthly_data, three_month_groups, "3-Month Total")
six_month_totals = group_precipitation(monthly_data, six_month_groups, "6-Month Total")
ten_month_totals = group_precipitation(monthly_data, ten_month_group, "10-Month Total")
twelve_month_totals = group_precipitation(monthly_data, twelve_month_group, "12-Month Total")

# SPI calculation function
def calculate_spi(data, column, method="log-normal"):
    values = data[column].dropna()
    if method == "log-normal":
        shape, loc, scale = lognorm.fit(values, floc=0)
        cdf = lognorm.cdf(values, shape, loc, scale)
    elif method == "normal":
        mean, std = norm.fit(values)
        cdf = norm.cdf(values, mean, std)
    elif method == "gumbel":
        loc, scale = gumbel_r.fit(values)
        cdf = gumbel_r.cdf(values, loc, scale)
    else:
        raise ValueError("Invalid method specified")
    
    cdf = np.clip(cdf, 1e-6, 1 - 1e-6)
    spi = norm.ppf(cdf)
    data[f"SPI ({method})"] = spi
    return data

# Add methods for SPI calculations
def calculate_all_spi(totals_list, column):
    for method in ["log-normal", "normal", "gumbel"]:
        for i, df in enumerate(totals_list):
            totals_list[i] = calculate_spi(df, column, method)

calculate_all_spi(one_month_totals, "1-Month Total")
calculate_all_spi(three_month_totals, "3-Month Total")
calculate_all_spi(six_month_totals, "6-Month Total")
calculate_all_spi([ten_month_totals[0]], "10-Month Total")
calculate_all_spi([twelve_month_totals[0]], "12-Month Total")

# Drought categories
categories = {
    "Very Wet": 2.0,
    "Wet": 1.5,
    "Moderately Wet": 0.5,
    "Moderately Dry": -0.5,
    "Severely Dry": -1.5,
    "Extremely Dry": -2.0
}

# Directory to save graphs
output_dir = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\spi-graph"
os.makedirs(output_dir, exist_ok=True)

# Combine SPI plots
def plot_combined_spi(totals_list, group_names, method, title, file_name, x_axis_label="Year", y_axis_label="SPI"):
    fig = go.Figure()

    # Add SPI data for each group to the figure
    for i, df in enumerate(totals_list):
        group_name = group_names[i]
        fig.add_trace(go.Bar(
            x=df["Year"],
            y=df[f"SPI ({method})"],
            name=group_name
        ))

    # Add drought category lines
    for category, value in categories.items():
        fig.add_trace(go.Scatter(
            x=totals_list[0]["Year"],
            y=[value] * len(totals_list[0]["Year"]),
            mode="lines",
            line=dict(dash="dot"),
            name=category
        ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_label,
        yaxis_title=y_axis_label,
        template="plotly_white",
        barmode='group'
    )

    # Save the figure as HTML
    fig.write_html(os.path.join(output_dir, f"{file_name}.html"))

# Group names for labeling
one_month_group_names = [g[0] for g in one_month_groups]
three_month_group_names = ["-".join(g) for g in three_month_groups]
six_month_group_names = ["-".join(g) for g in six_month_groups]
ten_month_group_names = ["-".join(g) for g in ten_month_group]
twelve_month_group_names = ["-".join(g) for g in twelve_month_group]

# Define methods for SPI calculation
methods = ["log-normal", "normal", "gumbel"]

# Plot for each method
for method in methods:
    # Combine 1-Month SPI data
    plot_combined_spi(
        one_month_totals,
        one_month_group_names,
        method,
        f"1-Month SPI Comparison ({method.capitalize()})",
        f"1-Month_SPI_Comparison_{method}"
    )

    # Combine 3-Month SPI data
    plot_combined_spi(
        three_month_totals,
        three_month_group_names,
        method,
        f"3-Month SPI Comparison ({method.capitalize()})",
        f"3-Month_SPI_Comparison_{method}"
    )

    # Combine 6-Month SPI data
    plot_combined_spi(
        six_month_totals,
        six_month_group_names,
        method,
        f"6-Month SPI Comparison ({method.capitalize()})",
        f"6-Month_SPI_Comparison_{method}"
    )

    # Combine 10-Month SPI data (only one group here)
    plot_combined_spi(
        [ten_month_totals[0]],
        ten_month_group_names,
        method,
        f"10-Month SPI Comparison ({method.capitalize()})",
        f"10-Month_SPI_Comparison_{method}"
    )

    # Combine 12-Month SPI data (only one group here)
    plot_combined_spi(
        [twelve_month_totals[0]],
        twelve_month_group_names,
        method,
        f"12-Month SPI Comparison ({method.capitalize()})",
        f"12-Month_SPI_Comparison_{method}"
    )
