import pandas as pd
import numpy as np
from scipy.stats import norm, lognorm, gumbel_r
import openpyxl

# Reading the data file
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Calculating the annual rainfall by summing the monthly rainfall
data['Total_Rainfall'] = data.iloc[:, 1:].sum(axis=1)

# Extracting the rainfall data
rainfall_data = data['Total_Rainfall']

# Fitting Normal, Log-Normal, and Gumbel distributions
normal_params = norm.fit(rainfall_data)
lognormal_params = lognorm.fit(rainfall_data, floc=0)  # floc=0 sets the zero location parameter for the log-normal distribution
gumbel_params = gumbel_r.fit(rainfall_data)

# Predicting the rainfall for an event with a return period of 120 years
percentile_120_years_normal = norm.ppf(1 - 1/120, *normal_params)
percentile_120_years_lognormal = lognorm.ppf(1 - 1/120, *lognormal_params)
percentile_120_years_gumbel = gumbel_r.ppf(1 - 1/120, *gumbel_params)

# Calculating the return period for a rainfall of 500 kg/m^2
prob_for_500_normal = norm.cdf(500, *normal_params)  
prob_for_500_lognormal = lognorm.cdf(500, *lognormal_params)
prob_for_500_gumbel = gumbel_r.cdf(500, *gumbel_params)

# Calculating the frequency in years
years_for_500_normal = 1 / (1 - prob_for_500_normal)
years_for_500_lognormal = 1 / (1 - prob_for_500_lognormal)
years_for_500_gumbel = 1 / (1 - prob_for_500_gumbel)

# Writing to Excel
result_df = pd.DataFrame({
    'Distribution': ['Normal', 'Log-Normal', 'Gumbel'],
    '120_years_rainfall': [percentile_120_years_normal, percentile_120_years_lognormal, percentile_120_years_gumbel],
    'Years_for_500_rainfall': [years_for_500_normal, years_for_500_lognormal, years_for_500_gumbel]
})

# Saving the result to an Excel file
result_df.to_excel(r"C:\Users\yasar\work_space\disrubition-and-frequency\tables\distrubition\rainfall_distribution_results.xlsx", index=False)

print("The results have been written to the Excel file.")
