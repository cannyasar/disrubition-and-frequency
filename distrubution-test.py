import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm, lognorm, gumbel_r
import os

# CSV dosyasını yükle
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Grafiklerin kaydedileceği dizin
graphs_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs\separate-dist-graphs"

# Excel in kaydedileceği dizin
os.makedirs(graphs_path, exist_ok=True)

# Excel sonuçları için sonuç sözlüğü
results = {
    "Month": [],
    "Year": [],
    "Probability (%)": [],
    "Qp_Normal": [],
    "Qp_LogNormal": [],
    "Qp_Gumbel": []
}

# Ay isimleri
months = data.columns[1:]  # İlk kolonun yıl bilgisi içerdiği varsayılır

# Her ay için grafik oluştur
for month in months:
    monthly_data = data[["Year", month]].dropna()
    if len(monthly_data) < 5:  # Yeterli veri olmadığında ayı geç
        print(f"Skipping {month} due to insufficient data.")
        continue

    sorted_data = monthly_data.sort_values(by=month)
    years = sorted_data["Year"].values
    precipitation = sorted_data[month].values

    n = len(precipitation)
    m = np.arange(1, n + 1)
    prob_q = m / (n + 1)  # Olasılık değeri m / (n + 1)

    # Normal dağılım parametreleri ve Qp hesaplaması
    mu, sigma = norm.fit(precipitation)
    qp_normal = norm.ppf(prob_q, loc=mu, scale=sigma)

    # Log-normal dağılım parametreleri ve Qp hesaplaması
    positive_data = precipitation[precipitation > 0]  # Pozitif veriler
    if len(positive_data) > 0:
        shape, loc, scale = lognorm.fit(positive_data, floc=0)
        qp_lognormal = lognorm.ppf(prob_q, shape, loc=loc, scale=scale)
    else:
        qp_lognormal = np.full_like(prob_q, np.nan)

    # Gumbel dağılım parametreleri ve Qp hesaplaması
    loc_gumbel, scale_gumbel = gumbel_r.fit(precipitation)
    qp_gumbel = gumbel_r.ppf(prob_q, loc=loc_gumbel, scale=scale_gumbel)

    # Negatif değerleri sıfıra çek
    qp_normal = np.maximum(qp_normal, 0)
    qp_lognormal = np.maximum(qp_lognormal, 0)
    qp_gumbel = np.maximum(qp_gumbel, 0)

    # Sonuçları sözlüğe ekle
    results["Month"].extend([month] * len(prob_q))
    results["Year"].extend(years)
    results["Probability (%)"].extend(prob_q * 100)
    results["Qp_Normal"].extend(qp_normal)
    results["Qp_LogNormal"].extend(qp_lognormal)
    results["Qp_Gumbel"].extend(qp_gumbel)

    # Normal dağılım grafiği (Y ekseni lineer)
    fig_normal = go.Figure()
    fig_normal.add_trace(go.Scatter(x=prob_q * 100, y=precipitation, mode='markers+lines', name='Normal Distribution',
                                    marker=dict(color='blue'),
                                    text=[f'Year: {y}<br>Probability: {p:.2f}%<br>Qp: {v:.2f}' for y, p, v in zip(years, prob_q * 100, precipitation)],
                                    hoverinfo='text'))
    fig_normal.update_layout(title=f'{month} Month - Normal Distribution',
                             xaxis_title='Probability (%)',
                             yaxis_title='Qp (kg/m²)',
                             xaxis=dict(type='log'),
                             template='plotly_dark')
    file_path_normal = os.path.join(graphs_path, f"{month}_normal_distribution_plot.html")
    fig_normal.write_html(file_path_normal)

    # Log-normal dağılım grafiği (Y ekseni logaritmik)
    if not np.isnan(qp_lognormal).all():
        fig_lognormal = go.Figure()
        fig_lognormal.add_trace(go.Scatter(x=prob_q * 100, y=qp_lognormal, mode='markers+lines', name='Log-Normal Distribution',
                                           marker=dict(color='green'),
                                           text=[f'Year: {y}<br>Probability: {p:.2f}%<br>Qp: {v:.2f}' for y, p, v in zip(years, prob_q * 100, qp_lognormal)],
                                           hoverinfo='text'))
        fig_lognormal.update_layout(title=f'{month} Month - Log-Normal Distribution',
                                    xaxis_title='Probability (%) - Logarithmic Scale',
                                    yaxis_title='Qp (kg/m²)',
                                    xaxis=dict(type='log'),
                                    yaxis=dict(type='log'),  # Y ekseni logaritmik
                                    template='plotly_dark')
        file_path_lognormal = os.path.join(graphs_path, f"{month}_lognormal_distribution_plot.html")
        fig_lognormal.write_html(file_path_lognormal)

    # Gumbel dağılım grafiği (Y ekseni lineer)
    fig_gumbel = go.Figure()
    fig_gumbel.add_trace(go.Scatter(x=prob_q * 100, y=qp_gumbel, mode='markers+lines', name='Gumbel Distribution',
                                    marker=dict(color='red'),
                                    text=[f'Year: {y}<br>Probability: {p:.2f}%<br>Qp: {v:.2f}' for y, p, v in zip(years, prob_q * 100, qp_gumbel)],
                                    hoverinfo='text'))
    fig_gumbel.update_layout(title=f'{month} Month - Gumbel Distribution',
                             xaxis_title='Probability (%)',
                             yaxis_title='Qp (kg/m²)',
                             xaxis=dict(type='log'),
                             template='plotly_dark')
    file_path_gumbel = os.path.join(graphs_path, f"{month}_gumbel_distribution_plot.html")
    fig_gumbel.write_html(file_path_gumbel)

# Sonuçları Excel dosyasına kaydet
results_df = pd.DataFrame(results)
excel_path = os.path.join(graphs_path, "distribution_results_with_years.xlsx")
results_df.to_excel(excel_path, index=False)
print(f"Results exported to {excel_path}")
