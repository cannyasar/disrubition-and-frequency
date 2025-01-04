import pandas as pd
import numpy as np
from scipy.stats import norm, lognorm, gumbel_r

# Reading the data
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Calculating total annual rainfall by summing monthly rainfall for each year
data['Total_Rainfall'] = data.iloc[:, 1:].sum(axis=1)

# Extracting the rainfall data for annual
rainfall_data = data['Total_Rainfall']

# Calculating Qmax and 1.5 Qmax
Q_max = rainfall_data.max()  # Maximum annual rainfall
Q_max_1_5 = 1.5 * Q_max     # 1.5 times Qmax

# Fitting Normal, Log-Normal, and Gumbel distributions to the total annual data
normal_params = norm.fit(rainfall_data)
lognormal_params = lognorm.fit(rainfall_data[rainfall_data > 0], floc=0)  # Remove non-positive values
gumbel_params = gumbel_r.fit(rainfall_data)

# --- 1) Monthly rainfall for 120-year return period for each distribution ---
monthly_rainfall_120_years = []
for month in data.columns[1:]:
    monthly_data = data[month]
    
    # Replace zero or negative values with a small positive value (e.g., 1e-6)
    monthly_data = monthly_data.replace(0, 1e-6)
    monthly_data[monthly_data < 0] = 1e-6  # Replace negatives with a small value
    
    # Fit distributions for the specific month
    month_normal_params = norm.fit(monthly_data)
    month_lognormal_params = lognorm.fit(monthly_data, floc=0)
    month_gumbel_params = gumbel_r.fit(monthly_data)
    
    # Calculate 120-year return period rainfall for each distribution
    monthly_rainfall_120_years.append({
        'Month': month,
        'Normal': norm.ppf(1 - 1/120, *month_normal_params),
        'Log-Normal': lognorm.ppf(1 - 1/120, *month_lognormal_params),
        'Gumbel': gumbel_r.ppf(1 - 1/120, *month_gumbel_params)
    })

# Convert to DataFrame for monthly rainfall
monthly_rainfall_df = pd.DataFrame(monthly_rainfall_120_years)

# --- 2) Total annual rainfall for 120-year return period for each distribution ---
percentile_120_years_normal = norm.ppf(1 - 1/120, *normal_params)
percentile_120_years_lognormal = lognorm.ppf(1 - 1/120, *lognormal_params)
percentile_120_years_gumbel = gumbel_r.ppf(1 - 1/120, *gumbel_params)

total_annual_rainfall_120_years = {
    'Normal': percentile_120_years_normal,
    'Log-Normal': percentile_120_years_lognormal,
    'Gumbel': percentile_120_years_gumbel
}

# --- 3) Total maximum rainfall (Qmax) for each distribution ---
total_max_rainfall_normal = Q_max  # Use Q_max for the maximum rainfall
total_max_rainfall_lognormal = Q_max
total_max_rainfall_gumbel = Q_max

total_max_rainfall = {
    'Normal': total_max_rainfall_normal,
    'Log-Normal': total_max_rainfall_lognormal,
    'Gumbel': total_max_rainfall_gumbel
}

# --- 1.5 Qmax Calculation ---
# Calculate 1.5 Qmax return period values for monthly, annual and max rainfall

# --- 4) Monthly rainfall for 1.5 Qmax return period for each distribution ---
monthly_rainfall_1_5_Qmax = []
for month in data.columns[1:]:
    monthly_data = data[month]
    
    # Replace zero or negative values with a small positive value (e.g., 1e-6)
    monthly_data = monthly_data.replace(0, 1e-6)
    monthly_data[monthly_data < 0] = 1e-6  # Replace negatives with a small value
    
    # Fit distributions for the specific month
    month_normal_params = norm.fit(monthly_data)
    month_lognormal_params = lognorm.fit(monthly_data, floc=0)
    month_gumbel_params = gumbel_r.fit(monthly_data)
    
    # Calculate 1.5 Qmax return period rainfall for each distribution
    monthly_rainfall_1_5_Qmax.append({
        'Month': month,
        'Normal': norm.ppf(1 - 1/(1 - norm.cdf(Q_max_1_5, *month_normal_params)), *month_normal_params),
        'Log-Normal': lognorm.ppf(1 - 1/(1 - lognorm.cdf(Q_max_1_5, *month_lognormal_params)), *month_lognormal_params),
        'Gumbel': gumbel_r.ppf(1 - 1/(1 - gumbel_r.cdf(Q_max_1_5, *month_gumbel_params)), *month_gumbel_params)
    })

# Convert to DataFrame for 1.5 Qmax monthly rainfall
monthly_rainfall_1_5_Qmax_df = pd.DataFrame(monthly_rainfall_1_5_Qmax)

# --- 5) Total annual rainfall for 1.5 Qmax return period for each distribution ---
total_annual_rainfall_1_5_Qmax = {
    'Normal': norm.ppf(1 - 1/(1 - norm.cdf(Q_max_1_5, *normal_params)), *normal_params),
    'Log-Normal': lognorm.ppf(1 - 1/(1 - lognorm.cdf(Q_max_1_5, *lognormal_params)), *lognormal_params),
    'Gumbel': gumbel_r.ppf(1 - 1/(1 - gumbel_r.cdf(Q_max_1_5, *gumbel_params)), *gumbel_params)
}

# --- 6) Total maximum rainfall (Qmax 1.5) for each distribution ---
total_max_rainfall_1_5_Qmax = {
    'Normal': Q_max_1_5,
    'Log-Normal': Q_max_1_5,
    'Gumbel': Q_max_1_5
}

# Writing results to Excel
with pd.ExcelWriter(r"C:\Users\yasar\work_space\disrubition-and-frequency\tables\distrubition\rainfall_distribution_results.xlsx") as writer:
    # --- 120 Year Return Period ---
    monthly_rainfall_df.to_excel(writer, sheet_name="120_Year_Monthly", index=False)
    pd.DataFrame([total_annual_rainfall_120_years]).to_excel(writer, sheet_name="120_Year_Annual", index=False)
    pd.DataFrame([total_max_rainfall]).to_excel(writer, sheet_name="120_Year_Total_Max_Rainfall", index=False)

    # --- 1.5 Qmax ---
    monthly_rainfall_1_5_Qmax_df.to_excel(writer, sheet_name="1_5_Qmax_Monthly", index=False)
    pd.DataFrame([total_annual_rainfall_1_5_Qmax]).to_excel(writer, sheet_name="1_5_Qmax_Annual", index=False)
    pd.DataFrame([total_max_rainfall_1_5_Qmax]).to_excel(writer, sheet_name="Total_Max_Rainfall_1_5_Qmax", index=False)

print("The results have been written to the Excel file.")
