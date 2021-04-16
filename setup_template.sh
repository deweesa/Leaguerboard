# Here is the template for a setup.sh filer for the enviorment.
# use:
#   Change the DATABASE_URL to whatever URL you need for local development
#   run `source setup.sh` to make these changes to you environement.
#
# !Note: You will also need to set an environment variable SECRET_KEY to 
# your Riot API Key if you're running anything that will make requests to
# the API.
. venv/bin/activate
export FLASK_APP=Leaguerboard
export FLASK_ENV=development
export DATABASE_URL="db_dialect://db_user:db_password@host:port/db"

