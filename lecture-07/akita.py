import requests
import json
import time
import sqlite3

APP_ID = 'YOUR_APP_ID'  
URL = 'https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426'
DB_NAME = 'rakuten_hotels.db'

def init_db():
    """データベースとテーブルを作成する"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # テーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            hotel_no INTEGER PRIMARY KEY,
            hotel_name TEXT,
            min_charge INTEGER,
            address TEXT,
            review_average REAL,
            hotel_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def fetch_and_save_all_hotels():
    conn = init_db()
    cursor = conn.cursor()
    
    # 基本パラメータ
    base_params = {
        'applicationId': APP_ID,
        'format': 'json',
        'largeClassCode': 'japan',
        'middleClassCode': 'akita',
        'smallClassCode': 'tazawa',
        'hits': 2,  
        'page': 1
    }

    print("--- データ収集を開始します ---")

    # --- 1. まず1ページ目を取得して、全体のページ数を把握 ---
    try:
        response = requests.get(URL, params=base_params)
        data = response.json()
        
        if response.status_code != 200:
            print(f"エラー発生: {response.status_code}")
            print(response.text)
            return

        # 全体の情報を取得
        record_count = data['pagingInfo']['recordCount']
        page_count = data['pagingInfo']['pageCount']
        
        print(f"検索ヒット総数: {record_count}件")
        print(f"総ページ数: {page_count}ページ")
        
    except Exception as e:
        print(f"初期通信エラー: {e}")
        return

    # --- 2. 各ページをループ処理 ---
    total_saved = 0
    
    for page in range(1, page_count + 1):
        print(f"\nProcessing page {page}/{page_count}...")
        
        # ページ番号をセット
        current_params = base_params.copy()
        current_params['page'] = page
        
        try:
            # 2ページ目以降のためにリクエスト（1ページ目は再取得しても良いし、さっきのdataを使っても良いが、ループ構造を単純にするため再取得）
            res = requests.get(URL, params=current_params)
            if res.status_code != 200:
                print(f"ページ{page}でエラー: {res.status_code}")
                continue
                
            page_data = res.json()
            hotels = page_data.get('hotels', [])
            
            # --- データベースへの保存 ---
            for hotel_wrapper in hotels:
                # データの抽出（存在しないキーがあってもエラーにならないよう .get を使用）
                basic = hotel_wrapper['hotel'][0]['hotelBasicInfo']
                rating = hotel_wrapper['hotel'][1].get('hotelRatingInfo', {}) 
                
                h_no = basic.get('hotelNo')
                h_name = basic.get('hotelName')
                h_price = basic.get('hotelMinCharge')
                h_addr = basic.get('address1', '') + basic.get('address2', '')
                h_url = basic.get('hotelInformationUrl')
                h_review = rating.get('serviceAverage') 
                
                # INSERT (REPLACEを使うと、同じIDがあった場合に上書きしてくれる)
                cursor.execute('''
                    INSERT OR REPLACE INTO hotels (hotel_no, hotel_name, min_charge, address, review_average, hotel_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (h_no, h_name, h_price, h_addr, h_review, h_url))
                
                total_saved += 1
            
            # ページごとにコミット（保存）
            conn.commit()
            print(f"  -> {len(hotels)}件保存完了 (累計: {total_saved}件)")

        except Exception as e:
            print(f"  -> エラー発生: {e}")

        # リクエスト過多を防ぐための待機
        if page < page_count:
            print("  -> 待機中(1秒)...")
            time.sleep(1)

    conn.close()
    print(f"\n=== 全処理完了 ===")
    print(f"合計 {total_saved} 件のデータを {DB_NAME} に保存しました。")

if __name__ == '__main__':
    fetch_and_save_all_hotels()