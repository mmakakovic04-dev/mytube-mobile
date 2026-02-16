import flet as ft
import os

def main(page: ft.Page):
    # Базовые настройки для мобилки
    page.title = "MyTube Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    
    # Мы убрали фиксированные размеры окна (window_width), 
    # чтобы Android не сходил с ума при запуске.

    # 1. Верхняя панель
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.PLAY_CIRCLE_FILL, color="red", size=30),
        title=ft.Text("MyTube", weight="bold"),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    # 2. Карточка видео
    def create_video_card(title, author):
        return ft.Container(
            content=ft.Column([
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
                )
            ]),
            margin=ft.margin.only(bottom=20)
        )

    video_feed = ft.Column(scroll="auto", expand=True)

    # 3. Безопасная загрузка контента (защита от белого экрана)
    try:
        video_dir = "uploads"
        # Создаем папку, если её нет, чтобы код не "падал"
        if not os.path.exists(video_dir):
            os.makedirs(video_dir, exist_ok=True)
            
        files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
        
        if not files:
            # Если видео нет, выводим дружелюбную надпись вместо ошибки
            video_feed.controls.append(
                ft.Container(
                    content=ft.Text("Интерфейс загружен! ✅\nВидео в папке 'uploads' не найдены.", 
                                  size=20, text_align="center"),
                    padding=50
                )
            )
        else:
            for file in files:
                video_feed.controls.append(create_video_card(file, "Admin"))
    except Exception as e:
        # Если случится любая другая ошибка — мы увидим её текст на экране
        video_feed.controls.append(ft.Text(f"Ошибка системы: {e}", color="red"))

    # 4. Нижнее меню
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME, label="Главная"),
            ft.NavigationDestination(icon=ft.icons.PLAY_CIRCLE_OUTLINE, label="Shorts"),
            ft.NavigationDestination(icon=ft.icons.SUBSCRIPTIONS_OUTLINED, label="Подписки"),
        ],
    )

    page.add(video_feed)

# Финальный запуск
ft.app(target=main)
