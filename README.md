# pyoslc

Python SDK for OSLC. Development project with Koneksys.


Installation on Windows:
Install Virtual Environment in the root of the project:

```
$ virtualenv venv
```


Activate the virtual environment using the activate batch script within the windows standard shell

```.env
$ .\venv\Scripts\activate.bat
```
 

For first usage install dependent libraries to your virtual environment

```
$ pip install -r requirements.txt
```

Set environment variables to configure and run the flask app

1. Configure the python script which creates the flask app (factory method)
    ```
    (venv) $ set FLASK_APP=ws-api
    ```

2. Configure the flask app mode (development with debugg information or production)
    ```
    (venv) $ set FLASK_ENV=development
    ```

3. Run the flask app
    ```.env
    (venv) $ flask run
    ```



Development of Flask Apps

Creating flask apps consist of following configurations:

1. Creating the app
    ```.python
    app = Flask(__name__, instance_relative_config=False)
    ```

2. Configure by file or configuration map
    ```.python
    config = {
        MAIL_SERVER=None,
        LOG_TO_STDOUT=None,
        SECRET_KEY='d3v3L0p',
        BASE_URI='http://examples.org/'
    }
    ```

3. Register Blueprints to endpoints
    
    A blueprint is an object that records functions that will be called with the 
    `:class:~flask.blueprints.BlueprintSetupState` later to register functions 
    or other things on the main application

Within the Blueprint Namesspaces and Services be defined to declare endpoint behaviours

4. Configure logging mechanisms


## Running Tests

For running the tests for the OSCL API implemented.

1. Go to the root `pyoslc` folder
    ```bash
    $ cd pyoslc
    ```

2. Run the tests
    ```python
    $ pytest
    ```
