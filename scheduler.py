from flask_apscheduler import APScheduler
from flask_mail import Message
from models.models import User, Task
from datetime import datetime
from pytz import timezone

scheduler = APScheduler()

def send_daily_tasklist(app, mail):
    with app.app_context():
        users = User.query.all()
        sender_email = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')

        for user in users:
            tasks = Task.query.filter_by(user_id=user.id).all()
            if not tasks:
                continue

            task_list = "\n".join(
                [f"- {t.title} (Due: {t.due_date.strftime('%Y-%m-%d %H:%M') if t.due_date else 'No due date'})"
                 for t in tasks]
            )

            msg = Message(
                subject="Your Daily Task List",
                sender=sender_email,
                recipients=[user.email],
                body=f"Hello,\n\nHere is your task list for today:\n\n{task_list}\n\nBest,\nYour To-Do App"
            )

            try:
                mail.send(msg)
                print(f"[Scheduler] Sent task list to {user.email}")
            except Exception as e:
                print(f"[Scheduler] Failed to send to {user.email}: {e}")

def init_scheduler(app, mail):
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(
        id='daily_tasklist',
        func=lambda: send_daily_tasklist(app, mail),
        trigger='cron',
        hour=10,
        minute=16,
        timezone=timezone('Asia/Kolkata')
    )
