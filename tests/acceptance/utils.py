import os
import shutil
from sqlalchemy import text
from deeptracy_core.dal.database import db


def clean_db(context):
    db.init_engine()
    clean_directory(context.SHARED_VOLUME_PATH)

    sql = text('DELETE FROM scan_analysis_vulnerability')
    context.engine.execute(sql)

    sql = text('DELETE FROM scan_analysis')
    context.engine.execute(sql)

    sql = text('DELETE FROM scan')
    context.engine.execute(sql)

    sql = text('DELETE FROM project')
    context.engine.execute(sql)

    # sql = text('DELETE FROM plugin')
    # context.engine.execute(sql)

    context.redis_db.delete('celery')


def clean_directory(folder: str):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
