Leaguerboard
============

Installation
------------

After cloning, create a virtual environment and install the requirements. 

    $ virualenv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt
    
Running
------

To run the flask app locally, first run the command

    $ source setup.sh
    
This sets the FLASK_APP, FLASK_ENV, and DATABASE_URL environment variables 
as well as activating the virtual enviornment. Be sure to change the 
DATABASE_URL in the setup_template.sh and copy to a file name `setup.sh`.

Then use

    (venv) $ flask run
    
to start the development server where you can access the site in your 
browser.
