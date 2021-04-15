#!/bin/bash
. venv/bin/activate
export FLASK_APP=Leaguerboard
export FLASK_ENV=development
export DATABASE_URL="postgresql://postgres:password@localhost:5432/leaguerboard"

