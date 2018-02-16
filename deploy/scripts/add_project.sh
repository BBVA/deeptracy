#!/bin/bash

source conf.sh

readonly ENDPOINT="$HOST/api/1/project/"

readonly JSON='
{
    "repo": "https://github.com/jspm/registry.git",
	"hook_type": "SLACK",
	"hook_data": {
		"webhook_url": "https://hooks.slack.com/services/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"
	}
}'

do_post() {
    echo ${JSON} | curl "$ENDPOINT" \
        -H "Content-Type:application/json" \
        --data @-
}

do_post

