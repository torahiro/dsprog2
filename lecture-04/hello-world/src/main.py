import flet as ft

# メイン関数
def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)
# ボタンが押された時に呼び出される関数
    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

        # -ボタンが押された時に呼び出される関数
    def increment_click(e):
        counter.data -= 1
        counter.value = str(counter.data)
        counter.update()

# カウンターを増やすボタンを追加
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    # SafeAreaを使って、カウンターを中央に配置
    page.add(   
        ft.SafeArea(
            ft.Container(
                counter,
                alignment=ft.alignment.center,
            ),
            expand=True,
        ),
        ft.FloatingActionButton(
        icon=ft.Icons.REMOVE, on_click=increment_click),
    )

ft.app(main)