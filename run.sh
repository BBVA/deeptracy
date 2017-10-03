#!/bin/bash

echo "RUNING CELERY"

celery -A deeptracy.celery:celery worker -l INFO
