# app.py
from app_init import create_app
from post_scheduler import start_scheduler

app = create_app()
start_scheduler(app)

if __name__ == '__main__':
    app.run(debug=True)
