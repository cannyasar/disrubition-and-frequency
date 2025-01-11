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

# Define period groups
one_month_groups = [["January"], ["February"], ["March"], ["April"], ["May"], ["June"], ["July"], ["August"], ["September"], ["October"], ["November"], ["December"]]
three_month_groups = [["January", "February", "March"], ["April", "May", "June"], ["July", "August", "September"], ["October", "November", "December"]]
six_month_groups = [["January", "February", "March", "April", "May", "June"], ["July", "August", "September", "October", "November", "December"]]
ten_month_group = [["September", "October", "November", "December", "January", "February", "March", "April", "May", "June"]]
twelve_month_group = [["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]]

# Group data by periods
def group_precipitation(data, groups, group_name):
    results = []
    for group in groups:
        grouped_data = data[data["Month"].isin(group)].groupby("Year")["Precipitation"].sum().reset_index()
        grouped_data.rename(columns={"Precipitation": group_name}, inplace=True)
        results.append(grouped_data)
    return results

one_month_totals = group_precipitation(monthly_data, one_month_groups, "1-Month Total")
three_month_totals = group_precipitation(monthly_data, three_month_groups, "3-Month Total")
six_month_totals = group_precipitation(monthly_data, six_month_groups, "6-Month Total")
ten_month_totals = group_precipitation(monthly_data, ten_month_group, "10-Month Total")
twelve_month_totals = group_precipitation(monthly_data, twelve_month_group, "12-Month Total")

# Directory to save graphs
output_dir = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\frequency-graphs"
os.makedirs(output_dir, exist_ok=True)

# Frequency Analysis Function with Normal, Log-Normal, and Gumbel
methods = ["normal", "log-normal", "gumbel"]
def frequency_analysis(data, column, method):
    values = data[column].dropna()

    # Fit the distribution
    if method == "log-normal":
        shape, loc, scale = lognorm.fit(values, floc=0)
        pdf = lognorm.pdf(np.sort(values), shape, loc, scale)
    elif method == "normal":
        mean, std = norm.fit(values)
        pdf = norm.pdf(np.sort(values), mean, std)
    elif method == "gumbel":
        loc, scale = gumbel_r.fit(values)
        pdf = gumbel_r.pdf(np.sort(values), loc, scale)
    else:
        raise ValueError("Invalid method specified")

    # Plot the histogram and fitted distribution
    fig = go.Figure()

    # Add histogram
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=15,
        histnorm='probability density',
        marker=dict(color='skyblue', line=dict(color='black', width=1)),
        name="Histogram"
    ))

    # Add fitted PDF line
    fig.add_trace(go.Scatter(
        x=np.sort(values),
        y=pdf,
        mode='lines',
        name=f"{method.capitalize()} Fit",
        line=dict(color='red')
    ))

    # Update layout
    fig.update_layout(
        title=f"Frequency Analysis ({method.capitalize()}) - {column}",
        xaxis_title="Precipitation",
        yaxis_title="Density",
        template="plotly_white",
        barmode="overlay"
    )

    # Save the plot
    file_name = f"{column.replace(' ', '_')}_{method}.html"
    fig.write_html(os.path.join(output_dir, file_name))

# Perform frequency analysis for each method and period
for method in methods:
    for period_totals, period_name in zip(
        [one_month_totals, three_month_totals, six_month_totals, [ten_month_totals[0]], [twelve_month_totals[0]]],
        ["1-Month Total", "3-Month Total", "6-Month Total", "10-Month Total", "12-Month Total"]):
        for period_data in period_totals:
            frequency_analysis(period_data, period_name, method)