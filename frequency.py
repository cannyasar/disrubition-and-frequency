import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Frequency and cumulative frequency validation function
def validate_frequencies(data, histogram, cumulative_freq, label):
    total_count = len(data)
    hist_sum = histogram.sum()
    cumulative_sum = cumulative_freq[-1]
    normalized_cumulative = cumulative_freq / hist_sum

    print(f"Validating: {label}")
    print(f"  Total Observations: {total_count}")
    print(f"  Histogram Total Frequency: {hist_sum} (Expected: {total_count})")
    print(f"  Cumulative Frequency Total: {cumulative_sum} (Should match Histogram Total)")
    print(f"  Normalized Cumulative Frequency Max: {normalized_cumulative[-1]} (Should be 1.0)")

    if hist_sum != total_count:
        print(f"  ERROR: Histogram total frequency does not match the total observations!")
        return False
    if cumulative_sum != hist_sum:
        print(f"  ERROR: Cumulative frequency does not match histogram total frequency!")
        return False
    if normalized_cumulative[-1] != 1:
        print(f"  ERROR: Normalized cumulative frequency does not reach 1.0!")
        return False
    print("Validation Complete.\n")
    return True

# Function to check for empty bins
def check_empty_bins(hist, bins, label):
    empty_bins = np.where(hist == 0)[0]
    result = {
        "Label": label,
        "Empty_Bins_Count": len(empty_bins),
        "Empty_Bins_Ranges": [(bins[idx], bins[idx + 1]) for idx in empty_bins]
    }
    return result

# Loading data
file_path = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\data\\precipitation_data.csv"
data = pd.read_csv(file_path)

# Selecting only the monthly precipitation columns (excluding the first column "Year" if it exists)
monthly_data = data.iloc[:, 1:]

# Calculating total annual rainfall and maximum annual rainfall
data['Total_Annual_Rainfall'] = monthly_data.sum(axis=1)
data['Max_Annual_Rainfall'] = monthly_data.max(axis=1)

# Setting values of 0 to 0.01 for log transformation
data['Total_Annual_Rainfall'] = data['Total_Annual_Rainfall'].apply(lambda x: x if x > 0 else 0.01)
data['Max_Annual_Rainfall'] = data['Max_Annual_Rainfall'].apply(lambda x: x if x > 0 else 0.01)

# Log transformation
log_total_rainfall = np.log10(data['Total_Annual_Rainfall'])
log_max_rainfall = np.log10(data['Max_Annual_Rainfall'])

# Histogram bins (20 bins)
bins_total_normal = np.linspace(data['Total_Annual_Rainfall'].min(), data['Total_Annual_Rainfall'].max(), 21)
bins_total_log = np.linspace(log_total_rainfall.min(), log_total_rainfall.max(), 21)

bins_max_normal = np.linspace(data['Max_Annual_Rainfall'].min(), data['Max_Annual_Rainfall'].max(), 21)
bins_max_log = np.linspace(log_max_rainfall.min(), log_max_rainfall.max(), 21)

# Frequency calculation
hist_total_normal, bin_edges_total_normal = np.histogram(data['Total_Annual_Rainfall'], bins=bins_total_normal)
hist_total_log, bin_edges_total_log = np.histogram(log_total_rainfall, bins=bins_total_log)

hist_max_normal, bin_edges_max_normal = np.histogram(data['Max_Annual_Rainfall'], bins=bins_max_normal)
hist_max_log, bin_edges_max_log = np.histogram(log_max_rainfall, bins=bins_max_log)

# Cumulative frequency calculation
cumulative_total_normal = np.cumsum(hist_total_normal)
cumulative_total_log = np.cumsum(hist_total_log)

cumulative_max_normal = np.cumsum(hist_max_normal)
cumulative_max_log = np.cumsum(hist_max_log)

# Checking for empty bins
empty_bins_total_normal = check_empty_bins(hist_total_normal, bin_edges_total_normal, "Total Annual Rainfall (Normal)")
empty_bins_total_log = check_empty_bins(hist_total_log, bin_edges_total_log, "Total Annual Rainfall (Log)")

empty_bins_max_normal = check_empty_bins(hist_max_normal, bin_edges_max_normal, "Max Annual Rainfall (Normal)")
empty_bins_max_log = check_empty_bins(hist_max_log, bin_edges_max_log, "Max Annual Rainfall (Log)")

# Reporting the results of empty bin analysis
print("\n--- Empty Bins Analysis ---")
print(empty_bins_total_normal)
print(empty_bins_total_log)
print(empty_bins_max_normal)
print(empty_bins_max_log)

# Validations
valid_total_normal = validate_frequencies(data['Total_Annual_Rainfall'], hist_total_normal, cumulative_total_normal, "Total Annual Rainfall (Normal)")
valid_total_log = validate_frequencies(log_total_rainfall, hist_total_log, cumulative_total_log, "Total Annual Rainfall (Log)")
valid_max_normal = validate_frequencies(data['Max_Annual_Rainfall'], hist_max_normal, cumulative_max_normal, "Max Annual Rainfall (Normal)")
valid_max_log = validate_frequencies(log_max_rainfall, hist_max_log, cumulative_max_log, "Max Annual Rainfall (Log)")

# Creating and saving graphs
if valid_total_normal and valid_total_log:
    # Graph for total annual rainfall
    fig_total = go.Figure()

    # Histogram for normal values (Total)
    fig_total.add_trace(go.Bar(
        x=bin_edges_total_normal[:-1],
        y=hist_total_normal,
        width=np.diff(bin_edges_total_normal),
        name='Normal Histogram (Total)',
        marker=dict(opacity=0.6, color='blue'),
        xaxis='x1',
        yaxis='y1'
    ))

    # Histogram for log values (Total)
    fig_total.add_trace(go.Bar(
        x=bin_edges_total_log[:-1],
        y=hist_total_log,
        width=np.diff(bin_edges_total_log),
        name='Log Histogram (Total)',
        marker=dict(opacity=0.6, color='green'),
        xaxis='x2',
        yaxis='y2'
    ))

    # Cumulative frequency for normal values (Total)
    fig_total.add_trace(go.Scatter(
        x=np.repeat(bin_edges_total_normal, 2)[1:-1],
        y=np.repeat(cumulative_total_normal, 2),
        mode='lines',
        name='Normal Cumulative (Total)',
        line=dict(color='blue', width=2),
        xaxis='x1',
        yaxis='y1'
    ))

    # Cumulative frequency for log values (Total)
    fig_total.add_trace(go.Scatter(
        x=np.repeat(bin_edges_total_log, 2)[1:-1],
        y=np.repeat(cumulative_total_log, 2),
        mode='lines',
        name='Log Cumulative (Total)',
        line=dict(color='green', width=2),
        xaxis='x2',
        yaxis='y2'
    ))

    # Axis settings
    fig_total.update_layout(
        title="Total Annual Rainfall: Normal and Log Comparisons",
        xaxis=dict(
            title="Rainfall (Normal Scale)",
            domain=[0, 1],
            side='bottom'
        ),
        xaxis2=dict(
            title="Rainfall (Logarithmic Scale)",
            domain=[0, 1],
            overlaying='x',
            side='top'
        ),
        yaxis=dict(
            title="Normal Scale Frequency",
            titlefont=dict(color="blue"),
            tickfont=dict(color="blue"),
            side="left"
        ),
        yaxis2=dict(
            title="Log Scale Frequency",
            titlefont=dict(color="green"),
            tickfont=dict(color="green"),
            overlaying="y",
            side="right"
        ),
        barmode='overlay',
        template='plotly_white'
    )

    # Saving the graph
    output_path_total = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\rainfall-total-normal-log-comparison.html"
    fig_total.write_html(output_path_total)
    print(f"Total rainfall graph saved at: {output_path_total}")

if valid_max_normal and valid_max_log:
    # Graph for maximum annual rainfall
    fig_max = go.Figure()

    # Histogram for normal values (Max)
    fig_max.add_trace(go.Bar(
        x=bin_edges_max_normal[:-1],
        y=hist_max_normal,
        width=np.diff(bin_edges_max_normal),
        name='Normal Histogram (Max)',
        marker=dict(opacity=0.6, color='red'),
        xaxis='x1',
        yaxis='y1'
    ))

    # Histogram for log values (Max)
    fig_max.add_trace(go.Bar(
        x=bin_edges_max_log[:-1],
        y=hist_max_log,
        width=np.diff(bin_edges_max_log),
        name='Log Histogram (Max)',
        marker=dict(opacity=0.6, color='orange'),
        xaxis='x2',
        yaxis='y2'
    ))

    # Cumulative frequency for normal values (Max)
    fig_max.add_trace(go.Scatter(
        x=np.repeat(bin_edges_max_normal, 2)[1:-1],
        y=np.repeat(cumulative_max_normal, 2),
        mode='lines',
        name='Normal Cumulative (Max)',
        line=dict(color='red', width=2),
        xaxis='x1',
        yaxis='y1'
    ))

    # Cumulative frequency for log values (Max)
    fig_max.add_trace(go.Scatter(
        x=np.repeat(bin_edges_max_log, 2)[1:-1],
        y=np.repeat(cumulative_max_log, 2),
        mode='lines',
        name='Log Cumulative (Max)',
        line=dict(color='orange', width=2),
        xaxis='x2',
        yaxis='y2'
    ))

    # Axis settings
    fig_max.update_layout(
        title="Max Annual Rainfall: Normal and Log Comparisons",
        xaxis=dict(
            title="Rainfall (Normal Scale)",
            domain=[0, 1],
            side='bottom'
        ),
        xaxis2=dict(
            title="Rainfall (Logarithmic Scale)",
            domain=[0, 1],
            overlaying='x',
            side='top'
        ),
        yaxis=dict(
            title="Normal Scale Frequency",
            titlefont=dict(color="red"),
            tickfont=dict(color="red"),
            side="left"
        ),
        yaxis2=dict(
            title="Log Scale Frequency",
            titlefont=dict(color="orange"),
            tickfont=dict(color="orange"),
            overlaying="y",
            side="right"
        ),
        barmode='overlay',
        template='plotly_white'
    )

    # Saving the graph
    output_path_max = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\graphs\\rainfall-max-normal-log-comparison.html"
    fig_max.write_html(output_path_max)
    print(f"Max rainfall graph saved at: {output_path_max}")

    fig_total.show()
    fig_max.show()
