#!/usr/bin/env bash

set -e

source ./.venv/bin/activate
flask --app flaskr init-db
