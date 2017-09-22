import os
import uuid
from celery import Celery
from celery.execute import send_task
from deeptracy.dal.database import db
from deeptracy.dal.models import Base

db.init_engine()
# Base.metadata.drop_all(bind=db.engine)
Base.metadata.create_all(bind=db.engine)

project_id = uuid.uuid4().hex
scab_id = uuid.uuid4().hex
# repo = 'https://github.com/MiniProfiler/node.git' # 0 v
repo = 'https://github.com/jspm/registry.git'


db.engine.execute("INSERT INTO project (id, repo) values ('{}', '{}')".format(project_id, repo))
db.engine.execute("INSERT INTO scan (id, project_id, lang) values ('{}', '{}', '{}')".format(scab_id, project_id, 'nodejs'))


BROKER_URI = os.environ.get('BROKER_URI')
print('connect to {}'.format(BROKER_URI))
celery = Celery('deeptracy',
                broker=BROKER_URI,
                backend=BROKER_URI,
                include=[
                    'deeptracy.tasks.start_scan',
                    'deeptracy.tasks.run_analyzer'
                ])

result = send_task("start_scan", [scab_id])
# result.get()
