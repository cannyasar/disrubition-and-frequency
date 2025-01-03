import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Verileri yükle
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Grafiklerin kaydedileceği dizin
graphs_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs\qp-pp"
os.makedirs(graphs_path, exist_ok=True)

# Aylar üzerinden işlem yapacağız
months = data.columns[1:]  # İlk sütun (Year) hariç tüm sütunlar ayları temsil eder

# Olasılık hesaplama fonksiyonu: 100 * m / (n + 1)
def calculate_probabilities(precipitation):
    n = len(precipitation)
    sorted_precipitation = np.sort(precipitation)
    return 100 * (np.arange(1, n + 1) / (n + 1))

# Grafikleri oluşturma: Her ay için
for month in months:
    monthly_data = data[["Year", month]].dropna()
    sorted_data = monthly_data.sort_values(by=month)
    precipitation = sorted_data[month].values  # Yağış verisi (Qp)
    years = sorted_data["Year"].values

    # Olasılık hesaplama
    probabilities = calculate_probabilities(precipitation)

    # Grafik oluşturma
    fig = go.Figure()

    # Yağış (Qp) vs Olasılık (PP) grafik
    fig.add_trace(go.Scatter(x=probabilities, y=precipitation, mode='markers+lines', name=month,
                             marker=dict(color='blue'),
                             text=[f'Year: {y}<br>Qp: {v:.2f}<br>Probability: {p:.2f}' for y, p, v in zip(years, probabilities, precipitation)],
                             hoverinfo='text'))

    # Grafik düzenlemeleri
    fig.update_layout(
        title=f'{month} Month - Rainfall vs Probability',
        xaxis_title='Probability (%) (Log Scale)',
        yaxis_title='Qp (kg/m²)',
        xaxis_type='log',  # X ekseni logaritmik
        template='plotly_dark'
    )
    
    # Grafik kaydetme
    file_path = os.path.join(graphs_path, f"{month}_rainfall_probability_plot.html")
    fig.write_html(file_path)

print("Grafikler başarıyla kaydedildi.")
