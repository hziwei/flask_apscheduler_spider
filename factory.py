from flask_apscheduler import APScheduler
from flask import Flask
scheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    # 配置任务，不然无法启动
    app.config.update(
        {"SCHEDULER_API_ENABLED": True,
         "JOBS": [{"id": "my_job",  # 任务ID
                   "func": "tasks:task",  # 任务位置
                   "trigger": "interval",  # 触发器
                   "seconds": 600,  # 时间间隔
                   }
                  ]}
    )
    scheduler.init_app(app)
    scheduler.start()
    return app
    pass

