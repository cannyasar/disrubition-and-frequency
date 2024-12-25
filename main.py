import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import mplcursors  # For adding interactive hover tooltips

# CSV dosyasını yükleme
file_path = r"C:\Users\yasar\OneDrive\Masaüstü\precipitation_data.csv"  # Dosya yolunu düzenleyin
df = pd.read_csv(file_path)

# Aylar listesi
months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

# Logaritmik eksen aralıkları (kullanıcı tarafından verilen sabitler)
log_intervals = [0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 30, 40, 50,
                 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8, 99.9, 99.99]

# Grafik çizimi
for month in months:
    # Ay verisi
    data = df[month].dropna()  # NaN değerleri kaldır
    data_sorted = np.sort(data)  # Verileri küçükten büyüğe sırala
    n = len(data_sorted)  # Veri sayısı
    m = np.arange(1, n + 1)  # Sıralama pozisyonları

    # Prob.q hesaplama
    prob_q = 100 * m / (n + 1)

    # Normal dağılım parametreleri
    mu, std = norm.fit(data_sorted)  # Ortalama ve standart sapmayı hesapla

    # Özel dönüşüm (logaritmik mesafeyi artırma)
    def custom_log_transform(x):
        """Logaritmik aralıkları genişletmek için dönüşüm"""
        return np.log10(x + 0.01) * 5  # 5 katsayısı ile mesafeler artırılır

    transformed_prob_q = custom_log_transform(prob_q)

    # Grafik oluşturma
    plt.figure(figsize=(14, 8))

    # Verilerin üzerini çizme
    scatter = plt.scatter(transformed_prob_q, data_sorted, color="red", label="Veri Noktaları", zorder=5)

    # Çizgiler ve etiketleme
    for x, y in zip(prob_q, data_sorted):
        transformed_x = custom_log_transform(x)
        # Dikey çizgiler
        plt.axvline(x=transformed_x, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)  # Dikey çizgi

    # X ekseni özel dönüşüm (etiketleme için log aralıkları)
    transformed_ticks = custom_log_transform(np.array(log_intervals))
    
    # Daha fazla mesafe eklemek için adım aralığını artırdım
    plt.xticks(transformed_ticks[::3], [f"{v:.2f}" for v in log_intervals][::3], rotation=0, fontsize=10)  # Daha az etiket göster

    # Y eksenini aritmetik tutmak ve Qp'yi y ekseninde göstermek
    plt.yscale('linear')
    plt.xlabel("Prob.q (%)", fontsize=12)
    plt.ylabel("Qp (m³/s)", fontsize=12)

    # Arka plan ızgarası
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.7)

    # Grafik başlık ve detaylar
    plt.title(f"{month} Ayı - Normal Dağılım ve Prob.q (X Ekseni Genişletilmiş Logaritmik)", fontsize=16)
    plt.legend()

    # Adjust text to avoid overlap
    plt.tight_layout()

    # Enable mplcursors for interactivity
    mplcursors.cursor(scatter, hover=True)

    # Show the plot
    plt.show()
