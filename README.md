# pyoslc

Python SDK for OSLC. Development project with Koneksys.


Installation on Windows:
Install Virtual Environment in the root of the project:
>>>virtualenv venv

Activate the virtual environment using the activate batch script within the windows standard shell
>>> .\venv\Scripts\activate.bat

For first usage install dependent libraries to your virtual environment
(venv) >>> pip install rdflib
(venv) >>> pip install rdflib-jsonld python-dotenv flask flask-restplus

Set environment variables to configure the flask app
    1. configure the python script which creates the flask app (factory method)
    2. configure the flask app mode (development with debugg information or production)
(venv) >>> set FLASK_APP=ws-api
(venv) >>> set FLASK_ENV=development

Run the flask app
(venv) >>> flask run


Development of Flask Apps
creating flask apps consist of follwing configurations:

1. Creating the app
app = Flask(__name__, instance_relative_config=False)

2. Configure by file or configuration map

3. Register Blueprints to endpoints
 A blueprint is an object that records functions that will be called with the :class:~flask.blueprints.BlueprintSetupState later to register functions or other things on the main application

Within the Blueprint Namesspaces and Services be defined to declare endpoint behaviours

4. Configure logging mechanisms


