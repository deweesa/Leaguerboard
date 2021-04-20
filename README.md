Leaguerboard
============

Installation
------------

After cloning, create a virtual environment and install the requirements. 

    $ virualenv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt
    
Running Locally
---------------

To run the flask app locally, first run the command

    $ source setup.sh
    
This sets the FLASK_APP, FLASK_ENV, and DATABASE_URL environment variables 
as well as activating the virtual enviornment. Be sure to change the 
DATABASE_URL in the setup_template.sh and copy to a file name `setup.sh`.

Then use

    (venv) $ flask run
    
to start the development server where you can access the site in your 
browser.

Managing the Database on Heroku
-------------------------------

If you're making major changes to the database hosted by Heroku, do not run 
processess that take a long time to complete (`$ flask populate_db` for example).
Make these changes locally then follow this guide on our [Wiki](https://github.com/deweesa/Leaguerboard/wiki/Uploading-Database-Backup-to-Heroku) 
or this guide on [Heroku's devcenter](https://devcenter.heroku.com/articles/heroku-postgres-import-export)
to push the database up to Heroku. And after doing this, geniunely, get up and walk away from the computer. 
It takes a while for the changes to go live, so do yourself a favor and don't keep refreshing the site
thinking "why is this broken".
