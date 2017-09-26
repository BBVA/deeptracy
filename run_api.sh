#!/bin/bash

echo "run api in ${SERVER_ADDRESS}"

# Run the web
gunicorn -w ${GUNICORN_WORKERS} deeptracy.flask:flask_app --bind ${SERVER_ADDRESS}
