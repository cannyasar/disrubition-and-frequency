import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm, lognorm, gumbel_r
import os

# Load the CSV file
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Directory to save the graphs and results
graphs_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs"
os.makedirs(graphs_path, exist_ok=True)

# Define the month names
months = data.columns[1:]  # Assumes the first column contains year information

# Logarithmic scale ticks
def get_log_ticks():
    return [0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8, 99.9, 99.99]

# Initialize a dictionary to store the results for exporting to Excel
results = {"Month": [], "Probability (%)": [], "Qp_Normal": [], "Qp_LogNormal": [], "Qp_Gumbel": []}

# Create graphs for each month
for month in months:
    # Get and sort monthly data
    monthly_data = data[month].dropna()
    if len(monthly_data) < 5:  # Ensure sufficient data for meaningful analysis
        print(f"Skipping {month} due to insufficient data.")
        continue

    sorted_data = np.sort(monthly_data)
    n = len(sorted_data)
    m = np.arange(1, n + 1)
    prob_q = m / (n + 1)  # Probability value m / (n + 1)

    # Normal distribution parameters and Qp calculation
    try:
        mu, sigma = norm.fit(sorted_data)
        qp_normal = norm.ppf(prob_q, loc=mu, scale=sigma)
    except Exception as e:
        print(f"Error fitting Normal distribution for {month}: {e}")
        qp_normal = np.full_like(prob_q, np.nan)

    # Log-normal distribution parameters and Qp calculation
    positive_data = sorted_data[sorted_data > 0]
    if len(positive_data) > 0:
        try:
            shape, loc, scale = lognorm.fit(positive_data, floc=0)
            qp_lognormal = lognorm.ppf(prob_q, shape, loc=loc, scale=scale)
        except Exception as e:
            print(f"Error fitting Log-Normal distribution for {month}: {e}")
            qp_lognormal = np.full_like(prob_q, np.nan)
    else:
        qp_lognormal = np.full_like(prob_q, np.nan)

    # Gumbel distribution parameters and Qp calculation
    try:
        loc_gumbel, scale_gumbel = gumbel_r.fit(sorted_data)
        qp_gumbel = gumbel_r.ppf(prob_q, loc=loc_gumbel, scale=scale_gumbel)
    except Exception as e:
        print(f"Error fitting Gumbel distribution for {month}: {e}")
        qp_gumbel = np.full_like(prob_q, np.nan)

    # Clip negative values on the Y-axis to zero
    qp_normal = np.maximum(qp_normal, 0)
    qp_lognormal = np.maximum(qp_lognormal, 0)
    qp_gumbel = np.maximum(qp_gumbel, 0)

    # Add results to the dictionary
    results["Month"].extend([month] * len(prob_q))
    results["Probability (%)"].extend(prob_q * 100)
    results["Qp_Normal"].extend(qp_normal)
    results["Qp_LogNormal"].extend(qp_lognormal)
    results["Qp_Gumbel"].extend(qp_gumbel)

    # Normal distribution graph (Y-axis arithmetic)
    fig_normal = go.Figure()
    fig_normal.add_trace(go.Scatter(x=prob_q * 100, y=qp_normal, mode='markers+lines', name='Normal Distribution',
                                    marker=dict(color='blue'),
                                    text=[f'Probability: {p:.2f}%<br>Qp: {v:.2f}' for p, v in zip(prob_q * 100, qp_normal)],
                                    hoverinfo='text'))
    fig_normal.update_layout(title=f'{month} Month - Normal Distribution',
                             xaxis_title='Probability (%) - Logarithmic Scale',
                             yaxis_title='Qp (m³/s) - Arithmetic Scale',
                             xaxis=dict(type='log', tickvals=get_log_ticks(), ticktext=[str(tick) for tick in get_log_ticks()]),
                             template='plotly_dark')
    fig_normal.show()
    file_path_normal = os.path.join(graphs_path, f"{month}_normal_distribution_plot.html")
    fig_normal.write_html(file_path_normal)

    # Log-normal distribution graph (X and Y axes logarithmic)
    if not np.isnan(qp_lognormal).all():
        fig_lognormal = go.Figure()
        fig_lognormal.add_trace(go.Scatter(x=prob_q * 100, y=qp_lognormal, mode='markers+lines', name='Log-Normal Distribution',
                                           marker=dict(color='green'),
                                           text=[f'Probability: {p:.2f}%<br>Qp: {v:.2f}' for p, v in zip(prob_q * 100, qp_lognormal)],
                                           hoverinfo='text'))
        fig_lognormal.update_layout(title=f'{month} Month - Log-Normal Distribution',
                                    xaxis_title='Probability (%) - Logarithmic Scale',
                                    yaxis_title='Qp (m³/s) - Logarithmic Scale',
                                    xaxis=dict(type='log', tickvals=get_log_ticks(), ticktext=[str(tick) for tick in get_log_ticks()]),
                                    yaxis=dict(type='log'),
                                    template='plotly_dark')
        fig_lognormal.show()
        file_path_lognormal = os.path.join(graphs_path, f"{month}_lognormal_distribution_plot.html")
        fig_lognormal.write_html(file_path_lognormal)

    # Gumbel distribution graph (X and Y axes logarithmic)
    if not np.isnan(qp_gumbel).all():
        fig_gumbel = go.Figure()
        fig_gumbel.add_trace(go.Scatter(x=prob_q * 100, y=qp_gumbel, mode='markers+lines', name='Gumbel Distribution',
                                        marker=dict(color='red'),
                                        text=[f'Probability: {p:.2f}%<br>Qp: {v:.2f}' for p, v in zip(prob_q * 100, qp_gumbel)],
                                        hoverinfo='text'))
        fig_gumbel.update_layout(title=f'{month} Month - Gumbel Distribution',
                                 xaxis_title='Probability (%) - Logarithmic Scale',
                                 yaxis_title='Qp (m³/s) - Logarithmic Scale',
                                 xaxis=dict(type='log', tickvals=get_log_ticks(), ticktext=[str(tick) for tick in get_log_ticks()]),
                                 yaxis=dict(type='log'),
                                 template='plotly_dark')
        fig_gumbel.show()
        file_path_gumbel = os.path.join(graphs_path, f"{month}_gumbel_distribution_plot.html")
        fig_gumbel.write_html(file_path_gumbel)

# Export results to an Excel file
results_df = pd.DataFrame(results)
excel_path = os.path.join(graphs_path, "distribution_results.xlsx")
results_df.to_excel(excel_path, index=False)
print(f"Results exported to {excel_path}")
