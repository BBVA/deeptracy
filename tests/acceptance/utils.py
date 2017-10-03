from sqlalchemy import text
from deeptracy_core.dal.database import db


def clean_db(context):
    db.init_engine()

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
