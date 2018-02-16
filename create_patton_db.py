import os
import subprocess
import time
import psycopg2
from psycopg2.errorcodes import DUPLICATE_DATABASE
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(os.environ['POSTGRES_URI'])
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
try:
    cur.execute('CREATE DATABASE patton')
    print("Base de datos patton creada correctamente")
    cmdInitDB = f"patton-server -C {os.environ['POSTGRES_URI']}/patton init-db"
    process = subprocess.Popen(cmdInitDB.split(), stdout=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(5)
    output, error = process.communicate()
except Exception as e:
    cur.close()
    conn.close()
    if e.pgcode == DUPLICATE_DATABASE:
        print(e)
        pass
    else:
        raise

cmdInitDB = f"patton-server -C {os.environ['POSTGRES_URI']}/patton serve"
process = subprocess.Popen(cmdInitDB.split(), stdout=subprocess.PIPE)
