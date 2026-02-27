from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Izinkan akses dari frontend

# Konfigurasi
API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo')  # 'demo' sebagai fallback
BASE_URL = "https://www.alphavantage.co/query"

# Cache untuk menyimpan data sementara
cache = {}
CACHE_DURATION = 300  # 5 menit dalam detik

# Daftar pair forex yang akan ditampilkan
FOREX_PAIRS = [
    {'symbol': 'XAUUSD', 'name': 'Gold / Emas'},
    {'symbol': 'EURUSD', 'name': 'Euro / US Dollar'},
    {'symbol': 'GBPUSD', 'name': 'British Pound / US Dollar'},
    {'symbol': 'USDJPY', 'name': 'US Dollar / Japanese Yen'},
    {'symbol': 'AUDUSD', 'name': 'Australian Dollar / US Dollar'},
    {'symbol': 'USDCAD', 'name': 'US Dollar / Canadian Dollar'},
    {'symbol': 'NZDUSD', 'name': 'New Zealand Dollar / US Dollar'},
    {'symbol': 'USDCHF', 'name': 'US Dollar / Swiss Franc'}
]

def get_from_cache(key):
    """Ambil data dari cache jika masih valid"""
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    return None

def save_to_cache(key, data):
    """Simpan data ke cache"""
    cache[key] = (data, time.time())

def analyze_sentiment_from_news(articles):
    """
    Analisis sentimen dari berita
    Mengembalikan persentase BUY, SELL, SIDEWAYS
    """
    if not articles:
        return {'buy': 33, 'sell': 33, 'sideways': 34}  # Default seimbang
    
    bullish = 0
    bearish = 0
    neutral = 0
    
    for article in articles[:20]:  # Ambil 20 berita terbaru
        # Dari Alpha Vantage, kita bisa dapat sentiment score
        sentiment_score = article.get('overall_sentiment_score', 0)
        
        if sentiment_score > 0.15:
            bullish += 1
        elif sentiment_score < -0.15:
            bearish += 1
        else:
            neutral += 1
    
    total = bullish + bearish + neutral
    if total == 0:
        return {'buy': 33, 'sell': 33, 'sideways': 34}
    
    return {
        'buy': round((bullish / total) * 100),
        'sell': round((bearish / total) * 100),
        'sideways': round((neutral / total) * 100)
    }

def get_market_news(symbol):
    """Ambil berita dari Alpha Vantage"""
    cache_key = f"news_{symbol}"
    cached = get_from_cache(cache_key)
    if cached:
        return cached
    
    # Mapping symbol untuk Alpha Vantage
    av_symbol = symbol
    if symbol == 'XAUUSD':
        av_symbol = 'GOLD'  # Alpha Vantage pakai GOLD untuk emas
    
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': av_symbol,
        'apikey': API_KEY,
        'limit': 50
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if 'feed' in data:
            save_to_cache(cache_key, data)
            return data
        else:
            print(f"Error response for {symbol}: {data}")
            return None
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return None

def get_current_price(symbol):
    """Ambil harga terkini (simulasi)"""
    # Karena Alpha Vantage gratis terbatas, kita gunakan data simulasi
    # untuk harga real-time
    import random
    base_prices = {
        'XAUUSD': 2345.60,
        'EURUSD': 1.0876,
        'GBPUSD': 1.2645,
        'USDJPY': 149.32,
        'AUDUSD': 0.6587,
        'USDCAD': 1.3589,
        'NZDUSD': 0.6089,
        'USDCHF': 0.8798
    }
    
    base = base_prices.get(symbol, 1.0000)
    # Fluktuasi kecil ±0.2%
    change = base * (random.uniform(-0.002, 0.002))
    return round(base + change, 4)

@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')

@app.route('/api/sentiment')
def get_all_sentiment():
    """API untuk mendapatkan semua data sentimen"""
    results = []
    
    for pair in FOREX_PAIRS:
        symbol = pair['symbol']
        
        # Ambil data berita
        news_data = get_market_news(symbol)
        
        # Analisis sentimen
        if news_data and 'feed' in news_data:
            sentiment = analyze_sentiment_from_news(news_data['feed'])
            
            # Ambil beberapa judul berita untuk ditampilkan
            headlines = []
            for article in news_data['feed'][:3]:
                headlines.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', ''),
                    'time': article.get('time_published', '')[:8],  # YYYYMMDD
                    'sentiment': article.get('overall_sentiment_label', 'Neutral')
                })
        else:
            # Data default jika API error
            sentiment = {'buy': 40, 'sell': 35, 'sideways': 25}
            headlines = []
        
        # Harga simulasi
        price = get_current_price(symbol)
        
        # Tentukan arah sentimen
        if sentiment['buy'] > sentiment['sell'] + 10:
            direction = 'BULLISH'
            direction_color = 'green'
        elif sentiment['sell'] > sentiment['buy'] + 10:
            direction = 'BEARISH'
            direction_color = 'red'
        else:
            direction = 'NEUTRAL'
            direction_color = 'yellow'
        
        results.append({
            'symbol': symbol,
            'name': pair['name'],
            'price': price,
            'sentiment': sentiment,
            'direction': direction,
            'direction_color': direction_color,
            'headlines': headlines,
            'last_update': datetime.now().strftime('%H:%M:%S')
        })
    
    return jsonify({
        'pairs': results,
        'total_pairs': len(results),
        'last_update': datetime.now().isoformat()
    })

@app.route('/api/sentiment/<symbol>')
def get_pair_sentiment(symbol):
    """API untuk detail satu pair"""
    symbol = symbol.upper()
    pair = next((p for p in FOREX_PAIRS if p['symbol'] == symbol), None)
    
    if not pair:
        return jsonify({'error': 'Pair not found'}), 404
    
    # Ambil data berita
    news_data = get_market_news(symbol)
    
    if news_data and 'feed' in news_data:
        sentiment = analyze_sentiment_from_news(news_data['feed'])
        
        # Detail artikel
        articles = []
        for article in news_data['feed'][:10]:
            articles.append({
                'title': article.get('title', ''),
                'source': article.get('source', ''),
                'url': article.get('url', '#'),
                'summary': article.get('summary', '')[:200] + '...',
                'sentiment_score': article.get('overall_sentiment_score', 0),
                'sentiment_label': article.get('overall_sentiment_label', 'Neutral'),
                'time': article.get('time_published', '')
            })
    else:
        sentiment = {'buy': 40, 'sell': 35, 'sideways': 25}
        articles = []
    
    price = get_current_price(symbol)
    
    return jsonify({
        'symbol': symbol,
        'name': pair['name'],
        'price': price,
        'sentiment': sentiment,
        'articles': articles,
        'last_update': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 MARKET SENTIMENT WEB APP")
    print("=" * 50)
    print(f"📊 API Key: {API_KEY[:5]}...{API_KEY[-5:] if len(API_KEY) > 10 else 'demo'}")
    print(f"📈 Total Pairs: {len(FOREX_PAIRS)}")
    print("=" * 50)
    print("🌐 Buka browser: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)