#!/bin/bash

source conf.sh

readonly ENDPOINT="$HOST/api/1/scan/"
readonly PROJECT_ID="${1}"

readonly JSON='
{
    "project_id": "'$PROJECT_ID'",
    "lang": "nodejs"
}'

do_post() {
    echo ${JSON} | curl "$ENDPOINT" \
        -H "Content-Type:application/json" \
        --data @-
}

do_post

