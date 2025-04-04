from app_init import create_app
from post_scheduler import start_scheduler  # ✅ 追加

app = create_app()
start_scheduler(app)  # ✅ アプリにスケジューラーを紐付けて起動
