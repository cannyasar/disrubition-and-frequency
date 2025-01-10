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

# Create SPI plots
methods = ["log-normal", "normal", "gumbel"]

# Example plot for a period (same plot for all methods)
def plot_spi_comparison(df, column, title, file_name, x_axis_label="Year", y_axis_label="SPI"):
    fig = go.Figure()

    for method in methods:
        fig.add_trace(go.Bar(
            x=df["Year"],
            y=df[f"SPI ({method})"],
            name=f"{method.capitalize()}"
        ))

    for category, value in categories.items():
        fig.add_trace(go.Scatter(
            x=df["Year"],
            y=[value] * len(df["Year"]),
            mode="lines",
            line=dict(dash="dot"),
            name=category
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_axis_label,
        yaxis_title=y_axis_label,
        template="plotly_white",
        barmode='group'
    )

    # Save the figure as HTML
    fig.write_html(os.path.join(output_dir, f"{file_name}.html"))

# 1-Month SPI plots
for i, df in enumerate(one_month_totals):
    month_name = one_month_groups[i][0]
    plot_spi_comparison(df, "1-Month Total", f"1-Month SPI ({month_name})", f"1-Month_SPI_{month_name}")

# 3-Month SPI plots
for i, df in enumerate(three_month_totals):
    months = ", ".join(three_month_groups[i])
    plot_spi_comparison(df, "3-Month Total", f"3-Month SPI ({months})", f"3-Month_SPI_{months.replace(', ', '_')}")

# 6-Month SPI plots
for i, df in enumerate(six_month_totals):
    months = ", ".join(six_month_groups[i])
    plot_spi_comparison(df, "6-Month Total", f"6-Month SPI ({months})", f"6-Month_SPI_{months.replace(', ', '_')}")

# 10-Month SPI plot
months = ", ".join(ten_month_group[0])
plot_spi_comparison(ten_month_totals[0], "10-Month Total", f"10-Month SPI ({months})", f"10-Month_SPI_{months.replace(', ', '_')}")

# 12-Month SPI plot
months = ", ".join(twelve_month_group[0])
plot_spi_comparison(twelve_month_totals[0], "12-Month Total", f"12-Month SPI ({months})", f"12-Month_SPI_{months.replace(', ', '_')}")
