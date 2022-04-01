# PyOSLC SDK

The `PyOSLC` project was developed as a set of classes and libraries 
packaged as an SDK which is aimed to build REST-based API’s that allows us 
to implement `OSLC (Open Services for Lifecycle Collaboration) projects`
that meet the specifications for creating REST services to enable 
the interoperability of heterogeneous products and services.

## Getting Started

The new version of `PyOSLC SDK` which is under development, has two ways to deploy
an OSLC API:

- *Pluggable API*: The OSLC API will be added to an existent Web API such as a CE Application or whichever REST API.
- *Standalone API*: The OSLC API will be implemented and should be executed isolated, this means that a web app or REST API will be created and deployed independently using the PyOSLC library to manage the OSLC resources.

## Working with PyOSLC

There are two ways to install the `PyOSLC SDK` to use it in your projects, the first one
is to download the code and install it in your local project, or the second one, to use
`pip` for installing it from the `GitHub` repository.

Let's create an example using the second approach.

### Creating a virtual environment

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

And this is how it looks using `virtualenv`

```shell
$ mkdir myproject
$ cd myproject
$ virtualenv myenv
created virtual environment CPython2.7.18.final.0-64 in 417ms
... 

$ source myenv/bin/activate
(myenv) $
```

### Installing PyOSLC

Once the virtual environment has been created it is time to install the framework 
to start working in the development of the API

```bash
(myenv) $ pip install git+https://github.com/cslab/pyoslc.git@develop
```

** Note: Keep your eyes in the `develop` tag of the url in the installation command

This command will download the `develop` branch of `PyOSLC SDK` from `GitHub` 
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
from pyoslc_server import OSLCAPP

app = OSLCAPP(name='oslc-app', prefix='/oslc')
```

The code above will create an `OSLCAPP` instance which is an OSLC API that will be 
processing the requests and will return RDF representation.

Now you can run the application by executing the following command:

```shell
(myenv) $ pyoslc run
 * Environment: development
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 ...
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

If you run a request against this server or navigate to the URL on your browser:

```shell
(myenv) $ curl -X GET http http://127.0.0.1:5000/oslc/services/catalog -H accept:"application/rdf+xml"
```

You will see a message like this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:oslc="http://open-services.net/ns/core#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <oslc:ServiceProviderCatalog rdf:about="http://127.0.0.1:5000/oslc/services/catalog">
    <dcterms:description>Service Provider Catalog for the PyOSLC application.</dcterms:description>
    <dcterms:title>Service Provider Catalog</dcterms:title>
  </oslc:ServiceProviderCatalog>
</rdf:RDF>
```

This is fine, this means that the OSLC API is working since the response is in RDF,
but it does not have yet an `Adapter` or `ServiceProvider` to work with, that is because 
it just returning the title and description for the Service Provider Catalog.

### Configuring the Environment variables

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
PYOSLC_APP=wsgi:app
PYOSLC_ENV=development
PYOSLC_DEBUG=True
```

Once the parameters have been configured it is time to continue developing the application

### Adding an Adapter to the PyOSLC Application

PyOSLC deploys the web server and the services for implementing the OSLC API
components, it is required now to plug the `Adapter` that will operate with the
`Resource` from the datasource.

#### Defining the Resource Type

The goal of the `Adapter` is to operate between the OSLC API and the datasource,
this means that the `Adapter` will operate with `resources` that could be Requirements,
Test Cases, Products, Documents, and so on.

So it is necessary to define the `Resource` class.

```shell
(myenv) $ vim resource.py
```

This module should define the resource type through a class to be used when exchanging
information:

```python
# -*- coding: utf-8 -*-

class Requirement(object):

    def __init__(self, identifier, title, description, creator):
        self.identifier = identifier
        self.title = title
        self.description = description
        self.creator = creator

REQSTORE = [
    Requirement("1", "Provide WSGI implementation", "...", "Yi"),
    Requirement("2", "Capability to add resources", "...", "Jörg"),
    Requirement("3", "Capability to manage paging", "...", "Christian"),
    Requirement("4", "Capability to use select properties", "...", "Arne"),
    Requirement("5", "Capability to specify page size", "...", "Torben"),
    # and so on ...
]
```

For the purpose of the demo, an in-memory list of requirements have been created
and will be used in the adapter to demonstrate how to retrieve information from
a datasource.

#### Defining the Adapter

Once the `Resource` class has been created, it is time to implement the `Adapter`
by adding a new python module.

```shell
(myenv) $ vim adapter.py
```

Within this file it is required to create a class that should extend from
`ServiceResourceAdapter` of `pyoslc_server.specification` package.

```python
from pyoslc_server.specification import ServiceResourceAdapter

from pyoslc.vocabularies.rm import OSLC_RM
from rdflib import DCTERMS
from resource import REQSTORE

class RequirementAdapter(ServiceResourceAdapter):
    
    domain = OSLC_RM
    items = REQSTORE
    
    def __init__(self, **kwargs):
        super(RequirementAdapter, self).__init__(**kwargs)
        self.types = [OSLC_RM.Requirement]
    
    def query_capability(self, paging=False, page_size=50, page_no=1,
                         prefix=None, where=None, select=None,
                         *args, **kwargs):
        return len(self.items), [self.convert_data(item) for item in self.items]
    
    def convert_data(self, item):
        return {
            "http://purl.org/dc/terms/identifier": item.identifier,
            "http://purl.org/dc/terms/description": item.description,
            "http://purl.org/dc/terms/title": item.title,
            "http://purl.org/dc/terms/creator": item.creator,
        }
```

This class it is importing some modules and classes from the RDFLib and
from the vocabularies defined for the OSLC specification.

The OSLC resource type is assigned in the initialization of the adapter in
the `self.types` property, for the demo purpose it will be `Requirement` from
the `RM` specification.

A domain also was assigned to the class to be managed in the process of generating the
ServiceProvider

And finally the `query_capability` method is implemented and defines some parameters,
these parameters will be sent by the OSLC APP to the adapter to use them for the
query operation.

##### Attributes Mapping

Keep your eyes in the `convert_data` method within the `RequirementAdapter` class,
since this method is converting the python object into a dictionary but most important
the attribute id is an IRI of the OSLC attribute.

On previous version of the SDK a dictionary was used to define the mapping of the 
OSLC attributes with the python object attribute.

This version delegate the responsability of this to the implementer by using the OSLC IRI
of the attribute as the name of the attribute.


### Attaching an Adapter to the PyOSLC Application

Finally, let's configure the initial OSLC APP on the `wsgi.py` file to attach the
adapter and to be able to see the Service Provider working.

```shell
(myenv) $ vim wsgi.py
```

Update the module with this content:

```python
from pyoslc_server import OSLCAPP
from adapter import RequirementAdapter

app = OSLCAPP()

requirement_adapter = RequirementAdapter(
    identifier='adapter',
    title='Requirement Adapter',
    description='Requirement Adapter for OSLC',
)

app.api.add_adapter(requirement_adapter)
```

#### Running the PyOSLC Application

To run the OSLC Application just call the `pyoslc` command line that will detect
the `OSLCAPP` instance and will deploy the application to start working with it.

```bash
(myenv) $ pyoslc run
* Serving PyOSLC app wsgi:app (lazy loading)
* Environment: development
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: off
2021-09-08 21:28:17,370 DEBUG: Initializing OSLC APP: <name: oslc-app> <prefix: /oslc> 
2021-09-08 21:28:18,370 DEBUG: Initializing OSLC API: <name: oslc-app> <prefix: /services> 
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

#### Requesting the PyOSLC Application

Since the example contains the `RequirementAdapter` class, it is possible to interact
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
    <oslc:domain rdf:resource="http://open-services.net/ns/rm#"/>
    <dcterms:description>Service Provider Catalog for the PyOSLC application.</dcterms:description>
    <dcterms:title>Service Provider Catalog</dcterms:title>
    <oslc:serviceProvider rdf:resource="http://localhost:5000/oslc/services/provider/adapter"/>
  </oslc:ServiceProviderCatalog>
</rdf:RDF>
```

Now the ServiceProvider is listed for the `RequirementAdapter`, let's see what is the
content of this endpoint.

```bash
(myenv) $ curl http://127.0.0.1:5000/oslc/services/provider/adapter -H accept:"application/rdf+xml"
```

Response:
```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:oslc="http://open-services.net/ns/core#">
  <oslc:ServiceProvider rdf:about="http://localhost:5000/oslc/services/provider/adapter">
    <dcterms:description>Requirement Adapter for OSLC</dcterms:description>
    <oslc:details rdf:resource="http://localhost:5000/oslc/services/provider/adapter"/>
    <dcterms:title rdf:parseType="Literal">Requirement Adapter</dcterms:title>
    <oslc:service>
      <oslc:Service rdf:nodeID="N4dc4132e4d8a4eb58ea47a795c8db373">
        <oslc:queryCapability>
          <oslc:QueryCapability rdf:nodeID="Nc393cc4c53464102939e5f544e53723b">
            <oslc:queryBase rdf:resource="http://localhost:5000/oslc/services/provider/adapter/resources"/>
            <dcterms:title>Query Capability</dcterms:title>
            <oslc:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Query Capability</oslc:label>
            <oslc:resourceShape rdf:resource="http://localhost:5000/oslc/services/resourceShapes/requirement"/>
            <oslc:resourceType rdf:resource="http://open-services.net/ns/rm#Requirement"/>
          </oslc:QueryCapability>
        </oslc:queryCapability>
        <oslc:domain rdf:resource="http://open-services.net/ns/rm#"/>
      </oslc:Service>
    </oslc:service>
    <dcterms:identifier rdf:datatype="http://www.w3.org/2001/XMLSchema#string">adapter</dcterms:identifier>
  </oslc:ServiceProvider>
</rdf:RDF>
```

In the response of the ServiceProvider endpoint, there is `Service` that contains the
definition of a `QueryCapability`, this service is available here since the `query_capability`
method was defined in the `RequirementAdapter` class, for each of these methods: `['query_capability', 
'creation_factory', 'selection_dialog', 'creation_dialog', 'get_resource']`, one service 
will be created.

Now, let's check what is the content of the `queryBase` endpoint of the OSLC API.

```bash
(myenv) $ curl http://127.0.0.1:5000/oslc/services/provider/adapter/resources -H accept:"application/rdf+xml"
```

Response:
```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:oslc="http://open-services.net/ns/core#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
  <oslc:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources">
    <rdfs:member rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/5"/>
    <rdfs:member rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/4"/>
    <rdfs:member rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/3"/>
    <rdfs:member rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/2"/>
    <rdfs:member rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/1"/>
  </oslc:Description>
</rdf:RDF>
```

Here is the list of resources defined on the in-memory list of requirements.

#### Requesting resources using paging and select

Since the Query Capability endpoint retrieves the list of resources within the 
datasource it is possible to use the pagination for getting specific number of 
resources, to do this, just add the `oslc.paging=true` query string parameters 
as defined in the specification.

By default, the pagination will return 50 resources per page, but it could be changed
by sending the `oslc.pageSize` parameter.

It is also possible to get specific attributes of the resources by using the `oslc.select`
in the query.

For more details you can see the [Query Syntax](https://archive.open-services.net/bin/view/Main/OSLCCoreSpecQuery)

For instance:

```bash
(myenv) $ curl http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.paging=true \
&oslc.pageSize=2 \
&oslc.pageNo=2 \
&oslc.select=dcterms:title \
-H accept:"application/rdf+xml"
```

Response:
```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:oslc="http://open-services.net/ns/core#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
  <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources">
    <rdfs:member>
      <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/4">
        <dcterms:title>Capability to select page</dcterms:title>
        <dcterms:identifier>4</dcterms:identifier>
      </rdf:Description>
    </rdfs:member>
    <rdfs:member>
      <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/3">
        <dcterms:title>Capability to paging</dcterms:title>
        <dcterms:identifier>3</dcterms:identifier>
      </rdf:Description>
    </rdfs:member>
  </rdf:Description>
  <oslc:ResponseInfo rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.pageSize=2&amp;oslc.pageNo=2&amp;oslc.paging=true">
    <oslc:totalCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">5</oslc:totalCount>
    <dcterms:title rdf:parseType="Literal">Query Results for Requirements</dcterms:title>
    <oslc:nextPage rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.pageNo=3&amp;oslc.pageSize=2&amp;oslc.paging=true"/>
  </oslc:ResponseInfo>
</rdf:RDF>
```

#### Requesting resources using where


It is also possible to get specific resources by using the `oslc.where`
in the query.

```bash
(myenv) $ curl http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.paging=true \
&oslc.pageSize=2 \
&oslc.pageNo=2 \
&oslc.where=dcterms:identifier=5\
-H accept:"application/rdf+xml"
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

### RDF Representation Format supported

Since PyOSLC is using `RDFLib` it supports the formats available
in this library and they are listed here:

- TriX
- [N-Quads](https://www.w3.org/TR/n-quads/)
- [TriG](http://www.w3.org/TR/trig/)
- [N3](https://www.w3.org/TeamSubmission/n3/)
- [N-Triples](http://www.w3.org/TR/rdf-testcases/#ntriples)
- [XML](https://www.w3.org/TR/rdf-syntax-grammar/)
- [Turtle](https://www.w3.org/TR/turtle/)
- [JSON-LD](https://json-ld.org)

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