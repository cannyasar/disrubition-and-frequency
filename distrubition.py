import pandas as pd
import numpy as np
import scipy.stats as stats

# Load the data
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Annual total rainfall (sum of all monthly rainfalls)
data_annual = data.drop(columns=["Year"]).sum(axis=1)

# Monthly total rainfall
monthly_rainfalls = data.drop(columns=["Year"]).sum(axis=0)

# Maximum rainfall (maximum rainfall value for each year)
data_maximum = data.drop(columns=["Year"]).max(axis=1)

# Determine Qmax and 1.5 Qmax values
qmax = data_maximum.max()
qmax_1_5 = 1.5 * qmax

# Writing to Excel
with pd.ExcelWriter(r"C:\Users\yasar\work_space\disrubition-and-frequency\tables\distrubition\precipitation_analysis.xlsx") as writer:

    # Normal Distribution Simulation
    mu_normal, std_normal = stats.norm.fit(data_annual)
    normal_monthly_rainfall = stats.norm.rvs(loc=mu_normal, scale=std_normal, size=(12, 1000)).mean(axis=1)
    normal_annual_rainfall = normal_monthly_rainfall.sum()
    normal_max_rainfall = normal_monthly_rainfall.max()

    # 1.5 Qmax for Normal Distribution
    p_qmax_normal = stats.norm.cdf(qmax_1_5, loc=mu_normal, scale=std_normal)
    return_period_qmax_normal = 1 / (1 - p_qmax_normal)

    # Writing data to Excel
    normal_df = pd.DataFrame({
        'January': normal_monthly_rainfall[0],
        'February': normal_monthly_rainfall[1],
        'March': normal_monthly_rainfall[2],
        'April': normal_monthly_rainfall[3],
        'May': normal_monthly_rainfall[4],
        'June': normal_monthly_rainfall[5],
        'July': normal_monthly_rainfall[6],
        'August': normal_monthly_rainfall[7],
        'September': normal_monthly_rainfall[8],
        'October': normal_monthly_rainfall[9],
        'November': normal_monthly_rainfall[10],
        'December': normal_monthly_rainfall[11],
        'Total Annual Rainfall': normal_annual_rainfall,
        'Maximum Rainfall': normal_max_rainfall,
        '1.5 Qmax Return Period (years)': return_period_qmax_normal
    }, index=["Normal Distribution"])

    normal_df.to_excel(writer, sheet_name='Normal Distribution')

    # LogNormal Distribution Simulation
    shape, loc, scale = stats.lognorm.fit(data_annual, floc=0)
    lognormal_monthly_rainfall = stats.lognorm.rvs(shape, loc, scale, size=(12, 1000)).mean(axis=1)
    lognormal_annual_rainfall = lognormal_monthly_rainfall.sum()
    lognormal_max_rainfall = lognormal_monthly_rainfall.max()

    # 1.5 Qmax for LogNormal Distribution
    p_qmax_lognormal = stats.lognorm.cdf(qmax_1_5, shape, loc, scale)
    return_period_qmax_lognormal = 1 / (1 - p_qmax_lognormal)

    # Writing data to Excel
    lognormal_df = pd.DataFrame({
        'January': lognormal_monthly_rainfall[0],
        'February': lognormal_monthly_rainfall[1],
        'March': lognormal_monthly_rainfall[2],
        'April': lognormal_monthly_rainfall[3],
        'May': lognormal_monthly_rainfall[4],
        'June': lognormal_monthly_rainfall[5],
        'July': lognormal_monthly_rainfall[6],
        'August': lognormal_monthly_rainfall[7],
        'September': lognormal_monthly_rainfall[8],
        'October': lognormal_monthly_rainfall[9],
        'November': lognormal_monthly_rainfall[10],
        'December': lognormal_monthly_rainfall[11],
        'Total Annual Rainfall': lognormal_annual_rainfall,
        'Maximum Rainfall': lognormal_max_rainfall,
        '1.5 Qmax Return Period (years)': return_period_qmax_lognormal
    }, index=["LogNormal Distribution"])

    lognormal_df.to_excel(writer, sheet_name='LogNormal Distribution')

    # Gumbel Distribution Simulation
    params = stats.gumbel_r.fit(data_annual)
    gumbel_monthly_rainfall = stats.gumbel_r.rvs(*params, size=(12, 1000)).mean(axis=1)
    gumbel_annual_rainfall = gumbel_monthly_rainfall.sum()
    gumbel_max_rainfall = gumbel_monthly_rainfall.max()

    # 1.5 Qmax for Gumbel Distribution
    p_qmax_gumbel = stats.gumbel_r.cdf(qmax_1_5, *params)
    return_period_qmax_gumbel = 1 / (1 - p_qmax_gumbel)

    # Writing data to Excel
    gumbel_df = pd.DataFrame({
        'January': gumbel_monthly_rainfall[0],
        'February': gumbel_monthly_rainfall[1],
        'March': gumbel_monthly_rainfall[2],
        'April': gumbel_monthly_rainfall[3],
        'May': gumbel_monthly_rainfall[4],
        'June': gumbel_monthly_rainfall[5],
        'July': gumbel_monthly_rainfall[6],
        'August': gumbel_monthly_rainfall[7],
        'September': gumbel_monthly_rainfall[8],
        'October': gumbel_monthly_rainfall[9],
        'November': gumbel_monthly_rainfall[10],
        'December': gumbel_monthly_rainfall[11],
        'Total Annual Rainfall': gumbel_annual_rainfall,
        'Maximum Rainfall': gumbel_max_rainfall,
        '1.5 Qmax Return Period (years)': return_period_qmax_gumbel
    }, index=["Gumbel Distribution"])

    gumbel_df.to_excel(writer, sheet_name='Gumbel Distribution')

    print("Data has been successfully saved to the Excel file.")
