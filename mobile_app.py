import flet as ft
import os


def main(page: ft.Page):
    page.title = "MyTube Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 400  # Делаем окно размером с телефон
    page.window_height = 700

    # 1. Верхняя панель (AppBar)
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.PLAY_CIRCLE_FILL, color="red", size=30),
        leading_width=40,
        title=ft.Text("MyTube", weight="bold", color="black"),
        bgcolor="white",
        actions=[
            ft.IconButton(ft.icons.SEARCH, icon_color="black"),
            ft.IconButton(ft.icons.NOTIFICATIONS_OUTLINED, icon_color="black"),
        ],
    )

    # 2. Функция создания карточки видео
    def create_video_card(title, author):
        return ft.Container(
            content=ft.Column([
                # Заглушка вместо видео (черный прямоугольник)
                ft.Container(
                    height=200,
                    bgcolor="black",
                    border_radius=12,
                    content=ft.Center(ft.Icon(ft.icons.PLAY_ARROW, color="white", size=50))
                ),
                ft.ListTile(
                    leading=ft.CircleAvatar(content=ft.Text(author[0])),
                    title=ft.Text(title, weight="bold"),
                    subtitle=ft.Text(f"{author} • 1.2 млн просмотров"),
                    trailing=ft.Icon(ft.icons.MORE_VERT),
                )
            ]),
            margin=ft.margin.only(bottom=20)
        )

    # 3. Список видео из твоей папки uploads
    video_feed = ft.Column(scroll="auto", expand=True, spacing=0)

    video_dir = "uploads"
    if os.path.exists(video_dir):
        files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
        if not files:
            video_feed.controls.append(ft.Text("Видео не найдены", size=20))
        for file in files:
            video_feed.controls.append(create_video_card(file, "Admin"))
    else:
        video_feed.controls.append(ft.Text("Папка uploads не найдена", size=20))

    # 4. Нижнее меню (Navigation Bar)
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME, label="Главная"),
            ft.NavigationDestination(icon=ft.icons.PLAY_CIRCLE_OUTLINE, label="Shorts"),
            ft.NavigationDestination(icon=ft.icons.ADD_CIRCLE_OUTLINE, label="", tooltip="Загрузить"),
            ft.NavigationDestination(icon=ft.icons.SUBSCRIPTIONS_OUTLINED, label="Подписки"),
            ft.NavigationDestination(icon=ft.icons.PERSON_OUTLINE, label="Вы"),
        ],
    )

    page.add(video_feed)


# Запускаем!
ft.app(target=main)