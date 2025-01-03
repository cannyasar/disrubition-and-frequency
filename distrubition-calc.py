import pandas as pd
import numpy as np
from scipy.stats import norm, lognorm, gumbel_r

# Verileri yükle
data = pd.read_csv(r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv")

# Aylar üzerinden işlem yapacağız
months = data.columns[1:]  # İlk sütun (Year) hariç tüm sütunlar ayları temsil eder

# Geri dönüş periyotları (Return Period) için olasılıklar
def return_period_to_probability(T):
    return 1 - 1 / T

# Olasılık -> Geri dönüş periyodu
def probability_to_return_period(prob):
    return 1 / (1 - prob)

# Normal Dağılım Parametreleri ve Hesaplamalar
def calculate_normal_discharge(T, precipitation):
    mu, sigma = norm.fit(precipitation)
    prob = return_period_to_probability(T)
    return norm.ppf(prob, loc=mu, scale=sigma)

# Log-Normal Dağılım Parametreleri ve Hesaplamalar
def calculate_lognormal_discharge(T, precipitation):
    positive_data = precipitation[precipitation > 0]
    shape, loc, scale = lognorm.fit(positive_data, floc=0)
    prob = return_period_to_probability(T)
    return lognorm.ppf(prob, shape, loc=loc, scale=scale)

# Gumbel Dağılım Parametreleri ve Hesaplamalar
def calculate_gumbel_discharge(T, precipitation):
    loc_gumbel, scale_gumbel = gumbel_r.fit(precipitation)
    prob = return_period_to_probability(T)
    return gumbel_r.ppf(prob, loc=loc_gumbel, scale=scale_gumbel)

# Tüm aylar için hesaplamalar
discharges_50_100_all_months = {}
return_periods_250_all_months = {}

# Excel'e yazılacak veri
results = []

for month in months:
    monthly_data = data[["Year", month]].dropna()
    sorted_data = monthly_data.sort_values(by=month)
    precipitation = sorted_data[month].values
    years = sorted_data["Year"].values
    
    # 50 ve 100 Yıllık Debiler
    discharges_50_100 = {
        "Normal": [calculate_normal_discharge(50, precipitation), calculate_normal_discharge(100, precipitation)],
        "LogNormal": [calculate_lognormal_discharge(50, precipitation), calculate_lognormal_discharge(100, precipitation)],
        "Gumbel": [calculate_gumbel_discharge(50, precipitation), calculate_gumbel_discharge(100, precipitation)],
    }
    
    discharges_50_100_all_months[month] = discharges_50_100
    
    # 250 m³/s için Geri Dönüş Periyodu
    target_discharge = 250

    def calculate_return_period(discharge, distribution, precipitation):
        if distribution == "Normal":
            mu, sigma = norm.fit(precipitation)
            prob = norm.cdf(discharge, loc=mu, scale=sigma)
        elif distribution == "LogNormal":
            positive_data = precipitation[precipitation > 0]
            shape, loc, scale = lognorm.fit(positive_data, floc=0)
            prob = lognorm.cdf(discharge, shape, loc, scale)
        elif distribution == "Gumbel":
            loc_gumbel, scale_gumbel = gumbel_r.fit(precipitation)
            prob = gumbel_r.cdf(discharge, loc=loc_gumbel, scale=scale_gumbel)
        else:
            raise ValueError("Unknown distribution.")
        return probability_to_return_period(prob)

    return_periods_250 = {
        "Normal": calculate_return_period(target_discharge, "Normal", precipitation),
        "LogNormal": calculate_return_period(target_discharge, "LogNormal", precipitation),
        "Gumbel": calculate_return_period(target_discharge, "Gumbel", precipitation),
    }
    
    return_periods_250_all_months[month] = return_periods_250
    
    # Excel için veriyi hazırlama
    for dist in ["Normal", "LogNormal", "Gumbel"]:
        results.append({
            "Month": month,
            "Distribution": dist,
            "50 Year Discharge": discharges_50_100[dist][0],
            "100 Year Discharge": discharges_50_100[dist][1],
            "Return Period for 250 m³/s (Years)": return_periods_250[dist],
        })

# Sonuçların Excel'e yazılması
df_results = pd.DataFrame(results)

# Excel dosyasını belirttiğiniz dizine kaydedin
output_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\tables\discharge-results\discharge_results.xlsx"
df_results.to_excel(output_path, index=False)

# Başarı mesajı
print(f"Sonuçlar Excel dosyasına başarıyla kaydedildi: {output_path}")
