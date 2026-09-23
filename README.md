# Market Sentiment Web App

Aplikasi web berbasis Flask untuk memantau sentimen pasar valuta asing dan emas secara real-time berdasarkan analisis berita finansial.

Aplikasi mengagregasi berita pasar terkini untuk berbagai pasangan mata uang utama, menghitung skor polaritas sentimen, dan menyajikannya dalam bentuk persentase probabilitas arah pergerakan harga.

## Fitur

- Pemantauan sentimen untuk 8 pasangan mata uang utama: XAUUSD, EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, dan USDCHF.
- Kalkulasi rasio persentase Buy, Sell, dan Sideways.
- Ticker berita finansial terkini dengan tautan artikel sumber.
- Pembaruan otomatis (auto-refresh) setiap 5 menit.
- Antarmuka responsif bertema gelap yang dioptimalkan untuk desktop maupun perangkat seluler.

## Instalasi

### Prasyarat

- Python 3.8 atau lebih baru
- pip

### Langkah Pemasangan

1. Clone repositori:
   ```bash
   git clone https://github.com/IlhamXkyo/sentimen-forex-web.git
   cd sentimen-forex-web
   ```

2. Buat dan aktifkan virtual environment:
   ```bash
   python -m venv venv
   # Di Windows:
   venv\Scripts\activate
   # Di Linux/macOS:
   source venv/bin/activate
   ```

3. Pasang paket dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurasi API Key:
   Salin berkas konfigurasi lingkungan dan masukkan kunci API Alpha Vantage milikmu:
   ```bash
   cp .env.example .env
   ```
   Isi parameter `ALPHA_VANTAGE_API_KEY` di dalam `.env`.

5. Jalankan server aplikasi:
   ```bash
   python app.py
   ```
   Buka peramban di `http://localhost:5000`.

## Struktur Direktori

```text
sentimen-forex-web/
├── app.py              # Server Flask utama dan penanganan rute
├── config.py           # Konfigurasi aplikasi dan variabel lingkungan
├── requirements.txt    # Daftar dependensi Python
├── services/
│   ├── news_fetcher.py # Modul pengambil berita pasar
│   └── sentiment.py    # Logika evaluasi sentimen
├── static/             # Aset statis (CSS, JavaScript)
└── templates/          # Berkas template Jinja2 HTML
```

## Lisensi

Didistribusikan di bawah lisensi MIT.
