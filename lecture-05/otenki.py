import flet as ft
import requests
import datetime

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1100
    page.window_height = 800

    # API設定
    AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
    FORECAST_URL_BASE = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

    weather_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=220,
        child_aspect_ratio=0.85,
        spacing=15,
        run_spacing=15,
        padding=20,
    )

    main_content = ft.Container(
        content=weather_grid,
        expand=True,
        bgcolor="#B0BEC5", 
    )

    def fetch_weather(e):
        area_code = e.control.data
        area_name = e.control.title.value
        
        weather_grid.controls.clear()
        page.snack_bar = ft.SnackBar(ft.Text(f"{area_name} のデータを取得中..."))
        page.snack_bar.open = True
        page.update()

        try:
            url = f"{FORECAST_URL_BASE}{area_code}.json"
            res = requests.get(url)
            data = res.json()

            target_data = data[1] if len(data) > 1 else data[0]
            
            weather_series = None
            temp_series = None
            for series in target_data["timeSeries"]:
                if "areas" in series and "weatherCodes" in series["areas"][0]:
                    weather_series = series
                if "areas" in series and ("temps" in series["areas"][0] or "tempsMin" in series["areas"][0]):
                    temp_series = series

            if not weather_series:
                weather_grid.controls.append(ft.Text("予報データが見つかりませんでした"))
                page.update()
                return

            dates = weather_series["timeDefines"]
            weather_codes = weather_series["areas"][0]["weatherCodes"]
            
            temps_min = []
            temps_max = []
            if temp_series:
                area_data = temp_series["areas"][0]
                if "tempsMin" in area_data:
                    temps_min = area_data["tempsMin"]
                    temps_max = area_data["tempsMax"]
                elif "temps" in area_data:
                    temps_max = area_data["temps"]
                    temps_min = ["-"] * len(temps_max)

            for i, date_str in enumerate(dates):
                dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d")

                w_code = weather_codes[i] if i < len(weather_codes) else ""
                
                # 文字で色指定
                icon_name = "help_outline"
                icon_color = "grey"
                weather_text = "予報"

                if w_code.startswith("1"):
                    icon_name = "wb_sunny"
                    icon_color = "orange"
                    weather_text = "晴れ"
                elif w_code.startswith("2"):
                    icon_name = "cloud"
                    icon_color = "grey"
                    weather_text = "曇り"
                elif w_code.startswith("3") or w_code.startswith("4"):
                    icon_name = "umbrella"
                    icon_color = "blue"
                    weather_text = "雨"
                elif w_code.startswith("5"):
                     icon_name = "ac_unit"
                     icon_color = "cyan"
                     weather_text = "雪"

                t_min = temps_min[i] if i < len(temps_min) and temps_min[i] != "" else "-"
                t_max = temps_max[i] if i < len(temps_max) and temps_max[i] != "" else "-"

                card = ft.Container(
                    content=ft.Column([
                        ft.Text(formatted_date, weight="bold", size=16),
                        ft.Icon(name=icon_name, size=50, color=icon_color),
                        ft.Text(weather_text, size=14, weight="bold"),
                        ft.Row(
                            [
                                ft.Text(f"{t_min}°C", color="blue"),
                                ft.Text("/", color="grey"),
                                ft.Text(f"{t_max}°C", color="red"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                    ),
                    bgcolor="white",
                    border_radius=10,
                    padding=20,
                    # 修正箇所: ここで ft.colors を使わずに直接色コードを使用
                    shadow=ft.BoxShadow(blur_radius=10, color="black") 
                )
                weather_grid.controls.append(card)

            page.update()

        except Exception as err:
            print(f"Error: {err}")
            page.snack_bar = ft.SnackBar(ft.Text(f"エラー: {err}"))
            page.snack_bar.open = True
            page.update()

    def create_sidebar():
        sidebar_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
        
        sidebar_column.controls.append(
            ft.Container(
                content=ft.Text("地域を選択", color="white", weight="bold"),
                padding=20,
                bgcolor="#37474F"
            )
        )

        try:
            response = requests.get(AREA_URL)
            area_data = response.json()
            centers = area_data["centers"]
            offices = area_data["offices"]

            for c_code, c_info in centers.items():
                children_widgets = []
                for child_code in c_info["children"]:
                    if child_code in offices:
                        o_name = offices[child_code]["name"]
                        children_widgets.append(
                            ft.ListTile(
                                title=ft.Text(o_name, color="white", size=14),
                                subtitle=ft.Text(child_code, color="#BDBDBD", size=12),
                                data=child_code,
                                on_click=fetch_weather,
                                bgcolor="#455A64",
                            )
                        )
                
                sidebar_column.controls.append(
                    ft.ExpansionTile(
                        title=ft.Text(c_info["name"], color="white"),
                        subtitle=ft.Text(c_code, color="#BDBDBD", size=12),
                        controls=children_widgets,
                        icon_color="white",
                        collapsed_icon_color="white",
                        bgcolor="transparent",
                    )
                )

        except Exception as e:
            sidebar_column.controls.append(ft.Text(f"Error: {e}", color="red"))

        return ft.Container(
            content=sidebar_column,
            width=250,
            bgcolor="#546E7A",
        )

    header = ft.Container(
        content=ft.Row([
            ft.Icon(name="wb_sunny", color="white"),
            ft.Text("天気予報", size=20, color="white", weight="bold"),
            ft.Container(expand=True),
            ft.Icon(name="more_horiz", color="white")
        ], alignment=ft.MainAxisAlignment.START),
        height=60,
        bgcolor="#311B92",
        padding=ft.padding.symmetric(horizontal=20)
    )

    page.add(header, ft.Row([create_sidebar(), main_content], expand=True, spacing=0))

ft.app(target=main)