# scheduler_command.py

from app_init import create_app
from post_scheduler import schedule_daily_articles

app = create_app()

if __name__ == "__main__":
    schedule_daily_articles(app)
