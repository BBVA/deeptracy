#!/bin/bash

echo "RUNING CELERY"

celery -A deeptracy.app:celery worker -l INFO
