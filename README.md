> :warning: **Warning** :warning: 
> 
> PyOSLC Announcement!
> 
> The PyOSLC SDK project is being improved!
> 
> The improvement will add some changes in the implementation of the SDK 
> to convert it into an OSLC Web Framework, this will change the way 
> to implement the API by adding better support for more data sources 
> by defining a neutral interface between OSLC API code, and data 
> source-specific access code. For adding a new data source, a developer 
> will only need to implement some adapter methods which are OSLC-independent. 
> This new behavior will allow us also to extend the domains in which 
> the API could work.
> 
> These improvements could represent some changes in the current version 
> that could affect your current implementation, our apology in advance.

# PyOSLC SDK

The `PyOSLC` project was developed as a set of classes and libraries 
packaged as an SDK which is aimed to build REST-based API’s that allows us 
to implement `OSLC (Open Services for Lifecycle Collaboration) projects`
that meet the specifications for creating REST services to enable 
the interoperability of heterogeneous products and services.

## Getting Started

The new version of `PyOSLC SDK` which is under development has two ways to deploy
OSLC API:

- *Pluggable API*: The OSLC API will be added to an existent Web API such as a CE Application.
- *Standalone API*: The OSLC API will be implemented and should be executed isolated.

### Working with PyOSLC

There are two ways to install the `PyOSLC SDK` to use it in your projects, the first one
is to download the code and install it in your local project, or the second one, to use
`pip` for installing it from the `Github` repository.

Let's create an example using the second approach.

#### Creating a virtual environment

To start using the `PyOSLC SDK` framework it should be installed, and it is
recommended to use a virtual environment for working with it.

Let's create the virtual environment using 
[`virtualenvwrapper`](https://virtualenvwrapper.readthedocs.io/en/latest/)

```bash
$ mkdir myproject
$ cd myproject
$ mkvirtualenv -python=`which python2.7` myenv
(myenv) $
```

#### Installing PyOSLC

Once the virtual environment has been created it is time to install the framework 
to start working in the development of the API

```bash
(myenv) $ pip install git+https://github.com/cslab/pyoslc.git@develop
```

** Note: Keep your eyes in the `develop` tag of the installation

This command will download the `develop` branch of `PyOSLC SDK` from `Github` 
repository and will build and install it in the current virtual environment
to enable the usage of the library including the CLI to execute the application
through the command line.

** Note: This is required so far since the `PyOSLC SDK` is not delivered on PyPI


### Creating a PyOSLC Application as Standalone API

Create a file in which the `OSLCAPP` should be instantiated, the file should be named
`wsgi.py` or `app.py` that will represent the executable that will be used for the 
command line to run the OSLC Application

```bash
(myenv) $ vim wsgi.py
```

Copy the next code within the file

```python
from apposlc.adapter import REQ_TO_RDF, RequirementAdapter
from pyoslc_server import OSLCAPP

app = OSLCAPP(name='oslc-app', prefix='/oslc')

app.api.add_adapter(
    identifier='adapter',
    title='Requirement Adapter',
    description='Requirement Adapter for OSLC',
    klass=RequirementAdapter,
    mapping=REQ_TO_RDF,
)
```

The code above will create an `OSLCAPP` instance which is a OSLC API that will be 
processing the requests and will return RDF representation of the ServiceProviderCatalog
and ServiceProvider depending on the configuration of the Adapter.

#### Configuring the Environment variables

Before the execution of the OSLC API, it is necessary to define some environment variables
that will specify which application should be executed and some other parameters for the
execution of the web application.

There are two ways for doing this:

1. Adding the parameters to the system environment
2. Defining the parameters using an `.env` or `.pyoslcenv` file

For the first approach use these commands

```bash
(myenv) $ export PYOSLC_APP=wsgi:app
(myenv) $ export PYOSLC_ENV=development
(myenv) $ export PYOSLC_DEBUG=True  
```

For the second approach

```bash
(myenv) $ vim .pyoslcenv 
```

Add the follow code within the file

```properties
PYOSLC_APP=apposlc.wsgi:app
PYOSLC_ENV=development
PYOSLC_DEBUG=True
```

Once the parameters have been configured it is time to execute the application

#### Running the PyOSLC Application

To run the OSLC Application just call the `pyoslc` command line that will detect
the `OSLCAPP` instance and will deploy the application to start working with it.

```bash
(myenv) $ pyoslc run
* Serving PyOSLC app apposlc.wsgi:app (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: off
2021-09-08 21:28:17,370 DEBUG: Initializing OSLC APP: <name: oslc-app> <prefix: /oslc> 
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

#### Requesting the PyOSLC Application

Since the example contains the `RequirementAdapter` example it is possible to interact
with the `OSLC API` to retrieve information from it.

For instance:

```bash
(myenv) $ curl http://127.0.0.1:5000/oslc/services/catalog -H accept:"application/rdf+xml"
```

Response:
```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:oslc="http://open-services.net/ns/core#">
  <oslc:ServiceProviderCatalog rdf:about="http://127.0.0.1:5000/oslc/services/catalog">
    <oslc:domain rdf:resource="http://open-services.net/ns/qm#"/>
    <oslc:serviceProvider rdf:resource="http://127.0.0.1:5000/oslc/services/tests"/>
    <oslc:serviceProvider rdf:resource="http://127.0.0.1:5000/oslc/services/adapter"/>
    <oslc:domain rdf:resource="http://open-services.net/ns/rm#"/>
    <dcterms:title>Service Provider Catalog</dcterms:title>
    <dcterms:description>Service Provider Catalog for the PyOSLC application.</dcterms:description>
  </oslc:ServiceProviderCatalog>
</rdf:RDF>
```

### Creating a PyOSLC Application as a Pluggable API

For demonstrating the pluggable application approach the repository includes
an example in the folder called `apposlc` that shows the different files required
for the deployment of the OSLC API.

- The `wsgi.py` file represents the `callable` for the web framework or web application.

- The `__init__.py` contains the instantiation of the web api.

- The `oslc_enabled.py` represents the web application in which the `OSLCAPP` should be added.

The execution of this application should be managed as defined in the web framework used
for the existent web api.
