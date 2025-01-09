import pandas as pd
import numpy as np
from scipy.stats import lognorm, norm
import plotly.graph_objects as go

# Veriyi yüklemek
file_path = r"C:\\Users\\yasar\\work_space\\disrubition-and-frequency\\data\\precipitation_data.csv"
data = pd.read_csv(file_path)

# Aylık verileri uzun formata dönüştürmek
monthly_data = data.melt(id_vars=["Year"], var_name="Month", value_name="Precipitation")
monthly_data["Month"] = pd.Categorical(
    monthly_data["Month"],
    categories=["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"],
    ordered=True
)
monthly_data.sort_values(by=["Year", "Month"], inplace=True)

# Sıfır veya negatif değerleri pozitif bir değere dönüştürme
monthly_data["Precipitation"] = monthly_data["Precipitation"].apply(lambda x: x if x > 0 else 0.01)

# Ay gruplarını belirleme
def group_precipitation(data, groups, group_name):
    results = []
    for group in groups:
        grouped_data = data[data["Month"].isin(group)].groupby("Year")["Precipitation"].sum().reset_index()
        grouped_data.rename(columns={"Precipitation": group_name}, inplace=True)
        results.append(grouped_data)
    return results

# Periyot gruplarını tanımlama
one_month_groups = [["January"], ["February"], ["March"], ["April"], ["May"], ["June"], ["July"], ["August"], ["September"], ["October"], ["November"], ["December"]]
three_month_groups = [["January", "February", "March"], ["April", "May", "June"], ["July", "August", "September"], ["October", "November", "December"]]
six_month_groups = [["January", "February", "March", "April", "May", "June"], ["July", "August", "September", "October", "November", "December"]]
ten_month_group = [["September", "October", "November", "December", "January", "February", "March", "April", "May", "June"]]
twelve_month_group = [["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]]

# Her periyot için toplam yağış hesaplama
one_month_totals = group_precipitation(monthly_data, one_month_groups, "1-Month Total")
three_month_totals = group_precipitation(monthly_data, three_month_groups, "3-Month Total")
six_month_totals = group_precipitation(monthly_data, six_month_groups, "6-Month Total")
ten_month_totals = group_precipitation(monthly_data, ten_month_group, "10-Month Total")
twelve_month_totals = group_precipitation(monthly_data, twelve_month_group, "12-Month Total")

# SPI hesaplama fonksiyonu
def calculate_spi(data, column):
    spi_results = []
    values = data[column].dropna()
    shape, loc, scale = lognorm.fit(values, floc=0)
    cdf = lognorm.cdf(values, shape, loc, scale)
    cdf = np.clip(cdf, 1e-6, 1 - 1e-6)
    spi = norm.ppf(cdf)
    spi_results.extend(spi)
    data["SPI"] = spi
    return data

# SPI hesaplamaları
for i, df in enumerate(one_month_totals):
    one_month_totals[i] = calculate_spi(df, "1-Month Total")

for i, df in enumerate(three_month_totals):
    three_month_totals[i] = calculate_spi(df, "3-Month Total")

for i, df in enumerate(six_month_totals):
    six_month_totals[i] = calculate_spi(df, "6-Month Total")

ten_month_totals[0] = calculate_spi(ten_month_totals[0], "10-Month Total")
twelve_month_totals[0] = calculate_spi(twelve_month_totals[0], "12-Month Total")

# Kuraklık kategorileri
categories = {
    "Çok Yağışlı": 2.0,
    "Yağışlı": 1.5,
    "Hafif Yağışlı": 0.5,
    "Hafif Kurak": -0.5,
    "Orta Kurak": -1.5,
    "Şiddetli Kurak": -2.0
}

# Ayrı ayrı SPI çubuk grafikleri oluşturmak
# 1 Aylık SPI grafikleri
for i, df in enumerate(one_month_totals):
    fig = go.Figure()
    month_name = one_month_groups[i][0]
    fig.add_trace(go.Bar(x=df["Year"], y=df["SPI"], name=f'1-Month SPI ({month_name})'))
    for category, value in categories.items():
        fig.add_trace(go.Scatter(
            x=df["Year"],
            y=[value] * len(df["Year"]),
            mode="lines",
            line=dict(dash="dot"),
            name=category
        ))
    fig.update_layout(
        title=f"1-Month SPI ({month_name}) [Log-Normal]",
        xaxis_title="Year",
        yaxis_title="SPI",
        template="plotly_white",
        barmode='group'
    )
    fig.show()

# 3 Aylık SPI grafikleri
for i, df in enumerate(three_month_totals):
    fig = go.Figure()
    months = ", ".join(three_month_groups[i])
    fig.add_trace(go.Bar(x=df["Year"], y=df["SPI"], name=f'3-Month SPI ({months})'))
    for category, value in categories.items():
        fig.add_trace(go.Scatter(
            x=df["Year"],
            y=[value] * len(df["Year"]),
            mode="lines",
            line=dict(dash="dot"),
            name=category
        ))
    fig.update_layout(
        title=f"3-Month SPI ({months}) [Log-Normal]",
        xaxis_title="Year",
        yaxis_title="SPI",
        template="plotly_white",
        barmode='group'
    )
    fig.show()

# 6 Aylık SPI grafikleri
for i, df in enumerate(six_month_totals):
    fig = go.Figure()
    months = ", ".join(six_month_groups[i])
    fig.add_trace(go.Bar(x=df["Year"], y=df["SPI"], name=f'6-Month SPI ({months})'))
    for category, value in categories.items():
        fig.add_trace(go.Scatter(
            x=df["Year"],
            y=[value] * len(df["Year"]),
            mode="lines",
            line=dict(dash="dot"),
            name=category
        ))
    fig.update_layout(
        title=f"6-Month SPI ({months}) [Log-Normal]",
        xaxis_title="Year",
        yaxis_title="SPI",
        template="plotly_white",
        barmode='group'
    )
    fig.show()

# 10 Aylık SPI grafiği
fig = go.Figure()
months = ", ".join(ten_month_group[0])
fig.add_trace(go.Bar(x=ten_month_totals[0]["Year"], y=ten_month_totals[0]["SPI"], name=f'10-Month SPI ({months})'))
for category, value in categories.items():
    fig.add_trace(go.Scatter(
        x=ten_month_totals[0]["Year"],
        y=[value] * len(ten_month_totals[0]["Year"]),
        mode="lines",
        line=dict(dash="dot"),
        name=category
    ))
fig.update_layout(
    title=f"10-Month SPI ({months}) [Log-Normal]",
    xaxis_title="Year",
    yaxis_title="SPI",
    template="plotly_white",
    barmode='group'
)
fig.show()

# 12 Aylık SPI grafiği
fig = go.Figure()
months = ", ".join(twelve_month_group[0])
fig.add_trace(go.Bar(x=twelve_month_totals[0]["Year"], y=twelve_month_totals[0]["SPI"], name=f'12-Month SPI ({months})'))
for category, value in categories.items():
    fig.add_trace(go.Scatter(
        x=twelve_month_totals[0]["Year"],
        y=[value] * len(twelve_month_totals[0]["Year"]),
        mode="lines",
        line=dict(dash="dot"),
        name=category
    ))
fig.update_layout(
    title=f"12-Month SPI ({months}) [Log-Normal]",
    xaxis_title="Year",
    yaxis_title="SPI",
    template="plotly_white",
    barmode='group'
)
fig.show()
