import flet as ft
import sqlite3
import requests

# 都市データ (47都道府県) 
LOCATIONS = {
    "北海道": {"HOKKAIDO": {"name": "北海道(札幌)", "lat": 43.0642, "lon": 141.3469, "code": "01"}},
    "東北": {
        "AOMORI": {"name": "青森", "lat": 40.8243, "lon": 140.7400, "code": "02"},
        "IWATE": {"name": "岩手", "lat": 39.7036, "lon": 141.1525, "code": "03"},
        "MIYAGI": {"name": "宮城(仙台)", "lat": 38.2682, "lon": 140.8694, "code": "04"},
        "AKITA": {"name": "秋田", "lat": 39.7186, "lon": 140.1025, "code": "05"},
        "YAMAGATA": {"name": "山形", "lat": 38.2404, "lon": 140.3633, "code": "06"},
        "FUKUSHIMA": {"name": "福島", "lat": 37.7503, "lon": 140.4675, "code": "07"},
    },
    "関東": {
        "IBARAKI": {"name": "茨城", "lat": 36.3417, "lon": 140.4467, "code": "08"},
        "TOCHIGI": {"name": "栃木", "lat": 36.5658, "lon": 139.8836, "code": "09"},
        "GUNMA": {"name": "群馬", "lat": 36.3907, "lon": 139.0633, "code": "10"},
        "SAITAMA": {"name": "埼玉", "lat": 35.8569, "lon": 139.6489, "code": "11"},
        "CHIBA": {"name": "千葉", "lat": 35.6074, "lon": 140.1065, "code": "12"},
        "TOKYO": {"name": "東京", "lat": 35.6895, "lon": 139.6917, "code": "13"},
        "KANAGAWA": {"name": "神奈川", "lat": 35.4477, "lon": 139.6425, "code": "14"},
    },
    "中部": {
        "NIIGATA": {"name": "新潟", "lat": 37.9022, "lon": 139.0236, "code": "15"},
        "TOYAMA": {"name": "富山", "lat": 36.6953, "lon": 137.2111, "code": "16"},
        "ISHIKAWA": {"name": "石川", "lat": 36.5944, "lon": 136.6256, "code": "17"},
        "FUKUI": {"name": "福井", "lat": 36.0652, "lon": 136.2219, "code": "18"},
        "YAMANASHI": {"name": "山梨", "lat": 35.6639, "lon": 138.5683, "code": "19"},
        "NAGANO": {"name": "長野", "lat": 36.6513, "lon": 138.1811, "code": "20"},
        "GIFU": {"name": "岐阜", "lat": 35.4233, "lon": 136.7606, "code": "21"},
        "SHIZUOKA": {"name": "静岡", "lat": 34.9769, "lon": 138.3831, "code": "22"},
        "AICHI": {"name": "愛知", "lat": 35.1802, "lon": 136.9067, "code": "23"},
    },
    "近畿": {
        "MIE": {"name": "三重", "lat": 34.7303, "lon": 136.5086, "code": "24"},
        "SHIGA": {"name": "滋賀", "lat": 35.0044, "lon": 135.8683, "code": "25"},
        "KYOTO": {"name": "京都", "lat": 35.0116, "lon": 135.7681, "code": "26"},
        "OSAKA": {"name": "大阪", "lat": 34.6937, "lon": 135.5023, "code": "27"},
        "HYOGO": {"name": "兵庫", "lat": 34.6913, "lon": 135.1830, "code": "28"},
        "NARA": {"name": "奈良", "lat": 34.6853, "lon": 135.8328, "code": "29"},
        "WAKAYAMA": {"name": "和歌山", "lat": 34.2260, "lon": 135.1675, "code": "30"},
    },
    "中国": {
        "TOTTORI": {"name": "鳥取", "lat": 35.5036, "lon": 134.2383, "code": "31"},
        "SHIMANE": {"name": "島根", "lat": 35.4722, "lon": 133.0506, "code": "32"},
        "OKAYAMA": {"name": "岡山", "lat": 34.6617, "lon": 133.9350, "code": "33"},
        "HIROSHIMA": {"name": "広島", "lat": 34.3853, "lon": 132.4553, "code": "34"},
        "YAMAGUCHI": {"name": "山口", "lat": 34.1783, "lon": 131.4736, "code": "35"},
    },
    "四国": {
        "TOKUSHIMA": {"name": "徳島", "lat": 34.0658, "lon": 134.5594, "code": "36"},
        "KAGAWA": {"name": "香川", "lat": 34.3403, "lon": 134.0433, "code": "37"},
        "EHIME": {"name": "愛媛", "lat": 33.8417, "lon": 132.7661, "code": "38"},
        "KOCHI": {"name": "高知", "lat": 33.5597, "lon": 133.5311, "code": "39"},
    },
    "九州・沖縄": {
        "FUKUOKA": {"name": "福岡", "lat": 33.5904, "lon": 130.4017, "code": "40"},
        "SAGA": {"name": "佐賀", "lat": 33.2636, "lon": 130.3008, "code": "41"},
        "NAGASAKI": {"name": "長崎", "lat": 32.7503, "lon": 129.8778, "code": "42"},
        "KUMAMOTO": {"name": "熊本", "lat": 32.8031, "lon": 130.7078, "code": "43"},
        "OITA": {"name": "大分", "lat": 33.2381, "lon": 131.6125, "code": "44"},
        "MIYAZAKI": {"name": "宮崎", "lat": 31.9077, "lon": 131.4203, "code": "45"},
        "KAGOSHIMA": {"name": "鹿児島", "lat": 31.5603, "lon": 130.5581, "code": "46"},
        "OKINAWA": {"name": "沖縄", "lat": 26.2124, "lon": 127.6809, "code": "47"},
    },
}

# WMO天気コードを日本語に変換する関数 
def get_weather_desc(code):
    if code == 0: return "快晴"
    if 1 <= code <= 3: return "晴れ/曇"
    if 45 <= code <= 48: return "霧"
    if 51 <= code <= 67: return "雨/しとしと雨"
    if 71 <= code <= 77: return "雪"
    if 80 <= code <= 82: return "にわか雨"
    if 95 <= code <= 99: return "雷雨"
    return "不明"

# データベースの初期化 
def init_db():
    with sqlite3.connect('weather_past.db') as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS regions (id INTEGER PRIMARY KEY, name TEXT)')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                code TEXT PRIMARY KEY, 
                name TEXT, 
                region_id INTEGER,
                lat REAL,
                lon REAL,
                FOREIGN KEY (region_id) REFERENCES regions(id)
            )
        ''')
        # forecast テーブルに temp_min カラムを追加
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT,
                report_date TEXT,
                weather_text TEXT,
                temp_max REAL,
                temp_min REAL,
                UNIQUE(area_code, report_date),
                FOREIGN KEY (area_code) REFERENCES areas(code)
            )
        ''')
        # 都市データを挿入
        for i, (r_name, prefs) in enumerate(LOCATIONS.items(), 1):
            cursor.execute('INSERT OR IGNORE INTO regions (id, name) VALUES (?, ?)', (i, r_name))
            for key, info in prefs.items():
                cursor.execute('INSERT OR IGNORE INTO areas (code, name, region_id, lat, lon) VALUES (?, ?, ?, ?, ?)', (info["code"], info["name"], i, info["lat"], info["lon"]))

# メイン関数
def main(page: ft.Page):
    page.title = "全国47都道府県 天気データ分析"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1100
    page.window_height = 800
    
    init_db()
    result_list = ft.ListView(expand=True, spacing=10, padding=20)

    # データベースからデータを取得して表示を更新する関数
    def refresh_view(area_code):
        result_list.controls.clear()
        with sqlite3.connect('weather_past.db') as conn:
            cursor = conn.cursor()
            # temp_min と weather_text も SELECT する
            cursor.execute('''
                SELECT areas.name, forecasts.report_date, forecasts.weather_text, forecasts.temp_max, forecasts.temp_min 
                FROM forecasts 
                JOIN areas ON forecasts.area_code = areas.code 
                WHERE areas.code = ?
                ORDER BY forecasts.report_date DESC
            ''', (area_code,))
            rows = cursor.fetchall()
            for row in rows:
                result_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"{row[0]} - {row[1]}", weight="bold", size=16),
                                    ft.Text(f"天気: {row[2]}", color="grey"),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(f"最高: {row[3]:.1f}°C", color="red", size=20, weight="bold"),
                                    ft.Text(f"最低: {row[4]:.1f}°C", color="blue", size=20, weight="bold"),
                                ], alignment=ft.MainAxisAlignment.START, spacing=30),
                            ]),
                            padding=15
                        )
                    )
                )
        page.update()
    # データ取得ボタンが押された時の処理
    def on_fetch(e):
        area_code = e.control.data
        flat_locs = {v["code"]: v for r in LOCATIONS.values() for k, v in r.items()}
        info = flat_locs[area_code]

        page.snack_bar = ft.SnackBar(ft.Text(f"{info['name']}のデータを取得中..."))
        page.snack_bar.open = True
        page.update()
        
        # データ取得とDB保存処理
        try:
            # temperature_2m_min と weather_code もリクエストに含める
            url = (f"https://archive-api.open-meteo.com/v1/archive?"
                   f"latitude={info['lat']}&longitude={info['lon']}&"
                   f"start_date=2025-12-20&end_date=2025-12-31&"
                   f"daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=Asia/Tokyo")
            
            res = requests.get(url).json()
            daily = res["daily"]
            
            with sqlite3.connect('weather_past.db') as conn:
                for i in range(len(daily["time"])):
                    # コードを日本語に変換
                    w_text = get_weather_desc(daily["weather_code"][i])
                    conn.execute('''
                        INSERT OR REPLACE INTO forecasts (area_code, report_date, weather_text, temp_max, temp_min) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (area_code, daily["time"][i], w_text, daily["temperature_2m_max"][i], daily["temperature_2m_min"][i]))
            
            refresh_view(area_code)
        except Exception as ex:
            print(f"Error: {ex}")

    # サイドバー作成（47都道府県リスト）
    def create_sidebar():
        sidebar_column = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        sidebar_column.controls.append(ft.Container(content=ft.Text("47都道府県リスト", color="white", weight="bold"), padding=20, bgcolor="#263238"))
        for r_name, prefs in LOCATIONS.items():
            tiles = [ft.ListTile(title=ft.Text(info["name"], color="white", size=13), data=info["code"], on_click=on_fetch) for key, info in prefs.items()]
            sidebar_column.controls.append(ft.ExpansionTile(title=ft.Text(r_name, color="white", size=14), controls=tiles, collapsed_icon_color="white", icon_color="white"))
        return ft.Container(content=sidebar_column, width=250, bgcolor="#37474F")

    page.add(
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.ANALYTICS, color="white"), ft.Text("全国過去天気データ分析ツール", size=20, color="white", weight="bold")]), bgcolor="#311B92", padding=20),
        ft.Row([create_sidebar(), ft.Container(content=result_list, expand=True, bgcolor="#F5F5F5")], expand=True, spacing=0)
    )

if __name__ == "__main__":
    ft.run(main)
