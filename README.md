# PyOSLC SDK

The `PyOSLC` project is developed as a set of classes and libraries 
packaged as an SDK which is aimed to build REST-based API’s that allows 
the implementation of `OSLC (Open Services for Lifecycle Collaboration) projects`
that meet the specifications for creating REST services to enable 
the interoperability of heterogeneous products and services.

The new version of `PyOSLC SDK`, it comes with two ways to deploy an OSLC API:

### *Pluggable API*
This means that a REST API already exist and requires to 
be extended for supporting the OSLC specification to manage the resources,
an instance of PyOSLC is created and added to the existent Web API.
(i.e. A CE Application or whichever REST API).

### *Standalone API*
This means that there is no REST API for managing resources
using OSLC, the usage of PyOSLC will create the web application and perform the 
routing to manage the REST + OSLC API, this service should be executed isolated,
this means that all the components will be created and deployed independently 
using the PyOSLC library to manage the OSLC resources.

## Introduction to PyOSLC

As mentioned before, PyOSLC is aimed to build REST-based APIs, 
thus it is prepared with a `server` package that contain the 
necessary classes to create a web server to manage the requests 
from the clients.


#### OSLC Web Application

The PyOSLC SDK has a class that will be used to create an OSLC Web Application. 
This class implements the required features to fit the [PEP 3333](https://peps.python.org/pep-3333/) 
for creating a web server and to manage the requests.

The `OSLCAPP` should be instantiated to create the web server and will
enable the endpoints for the discoverability of the resources based on
the OSLC specifications.

Once the `OSLCAPP` is instantiated the providers of resources could be added
to it for the exposure of the data. The providers will be called `Adpaters` for
the purpose of the implementation.

#### Service Providers

As part of the [OSLC specification](https://archive.open-services.net/bin/view/Main/OslcCoreSpecification.html)
there is a set of endpoints that should be available to discover and manage the 
resources exposed by an OSLC API.

In the image below there are three main components that it is important to keep
in mind when developing an OSLC API using PyOSLC: `Service Provider Catalog`,
`Service Provider` and `Service`.


##### Diagram of OSLC v2.0

[![OSCL v2.0](https://archive.open-services.net/pub/Main/OSLCCoreSpecDRAFT/oslc-core-overview.png)](https://archive.open-services.net/pub/Main/OSLCCoreSpecDRAFT/oslc-core-overview.png)


The `Service Provider Catalog` endpoint is created by default when the `OSLCAPP` is
instantiated from PyOSLC.

The `Service Provider` and its `Services` are an important component that should
be implemented by the developer, since this are the endpoints that will be interacting
with the data store (which the PyOSLC is agnostic of). 

The implementation of the `Services` for a `ServiceProvider` will be a task
that could be achieved by overwriting some methods of a class that comes in the `server`
package of PyOSLC.

#### Adapter

As mentioned in the above paragraph, the Service Provider component of OSLC
defines the services available for finding and creating resources in the data store
using OSLC.

This means that it requires to implement the main methods of the REST API
defined as GET, POST, PUT and so on, these methods have their corresponding
service name in the OSLC specification such as Query Capability or Creation Factory.

PyOSLC facilitates the implementation of these methods by implementing an `Adapter` class
which should overwrite a set of predefined methods to enable the features for
interact with the data store through the Query Capability (GET) or Creation Factory (POST)
services.

To implement an `Adapter` the developer should extend the class `ServiceResourceAdapter`
which comes in the `pyolsc-server` package. This class will be the one that will
implement most of the methods required for the discoverability and the management
of the data.

All these methods will be explained in the next section by using PyOSLC to implement
an OSLC API as an example.

## Working with PyOSLC

Since the project is still under development, it is not packaged and published yet in
[PyPI](https://pypi.org). To install and use the `PyOSLC SDK`, it should be necessary 
to install it from the `GitHub` repository using `pip`.

Let's create an example.

### Preparing the environment

It is highly recommended to use virtual environments when working with python projects,
so this is not an exception, let's create a virtual environment to start using 
the `PyOSLC SDK` framework.

There are different tools to create virtual environment, for this example
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) and
[virtualenv](https://virtualenv.pypa.io/en/latest/) will be used.

> *Note 1*: The project will be created using Python 2.7 just for an illustrative 
> way for using PyOSLC with this version of Python.

> *Note 2*: For macOS users, since Python 2.7 is no longer available for newer version
> of macOS, Pyenv could be used to install this version of Python.

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

Keep your eyes in the `develop` tag of the url in the installation command. 
This command will download the `develop` branch of `PyOSLC SDK` from `GitHub` 
repository and will build and install it in the current virtual environment
to enable the usage of the library including the `CLI` to execute the application
through the command line.

This is required so far since the `PyOSLC SDK` is not delivered on PyPI, 
once the project is released and published in PyPI the installation will be just 
by using the name of the library as usual.


### Creating a PyOSLC Application as Standalone API

Create a file in which the `OSLCAPP` should be instantiated, give it the name
`wsgi.py` or `app.py`, this file represents the executable to be used for the 
command line to run the OSLC Application

```bash
(myenv) $ vim wsgi.py
```

Copy the next code within the file

```python
from pyoslc_server import OSLCAPP

app = OSLCAPP(name='oslc-app', prefix='/oslc')
```

The above code will create an `OSLCAPP` instance which is an OSLC API. This application
could be used either to run a standalone web server or to be plugged into an existent
REST API.

The OSLC application will manage the requests for the endpoints established in the OSLC spec
and the serialization of the date to return the responses in their RDF representation.

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

If you send a request against this server or navigate to the URL in your web browser:

```shell
(myenv) $ curl -X GET http://127.0.0.1:5000/oslc/services/catalog -H accept:"application/rdf+xml"
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

The response contains the RDF representation of the Service Provider Catalog, that means that
the OSLC API is working, but it does not have yet an `Adapter` or `ServiceProvider` to work with, 
that is because it is just returning the title and description for the Service Provider Catalog.

Let's add an Adapter to the application

### Configuring the Environment variables

Since the example will use the command line interface (CLI) for the execution of the OSLC API,
it is necessary to define some environment variables that will specify which application
should be executed and some other parameters for the execution of the web application.

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

### Adding the Adapter

As mentioned before, the `OSLCAPP` instance only creates the API to have the 
capability to create the endpoints for the discoverability and the serialization
of the responses.

Now it is required to create a new class to extend the required methods for the
exposure of the data, this will be by extending the `ServiceResourceAdapter` class
and add the `Adapter` to the OSLC application to manage the resources from the datasource.

There are some steps required to complete the `Adapter` implementation.

#### Defining the Resource Type

The goal of the `Adapter` is to operate between the OSLC API and the datasource,
this means that the `Adapter` will operate with `resources` that could be Requirements,
Test Cases, Products, Documents, and so on.

So it is necessary to create a module in which the `Resource` classes will be defined.

```shell
(myenv) $ vim resource.py
```

This module should define the resource type through a class to be used when exchanging
information:

```python
# -*- coding: utf-8 -*-

class Creator:

    def __init__(self, identifier, first_name, last_name):
        self.identifier = identifier
        self.first_name = first_name
        self.last_name = last_name

CREATORSTORE = [
    Creator("1", "Yi", "Chen"),
    Creator("2", "Jörg", "Kollman"),
    Creator("3", "Christian", "Muggeo"),
    Creator("4", "Arne", "Kiel"),
    Creator("5", "Torben", "Hansing"),
    Creator("6", "Ian", "Altman"),
    Creator("7", "Frank", "Patz-Brockmann"),
]
        
class Requirement(object):

    def __init__(self, identifier, title, description, creator):
        self.identifier = identifier
        self.title = title
        self.description = description
        self.creator = creator
        self.discipline = [
            {
                "https://contact-software.com/ontologies/v1.0/plm#text": "Leistungsbedarf",
                "https://contact-software.com/ontologies/v1.0/plm#language": "de",
            },
            {
                "https://contact-software.com/ontologies/v1.0/plm#text": "Power Requirement",
                "https://contact-software.com/ontologies/v1.0/plm#language": "en",
            },
        ]

REQSTORE = [
    Requirement("1", "Provide WSGI implementation", "...", CREATORSTORE[0]),
    Requirement("2", "Capability to add resources", "...", CREATORSTORE[1]),
    Requirement("3", "Capability to manage paging", "...", CREATORSTORE[2]),
    Requirement("4", "Capability to use select properties", "...", CREATORSTORE[3]),
    Requirement("5", "Capability to specify page size", "...", CREATORSTORE[4]),
    # and so on ...
]
```

For the purpose of the demo, an in-memory list of requirements and creators 
have been created and will be used in the adapter to demonstrate how to retrieve 
information from the datasource.

> The resource module could be a package if needed and have different modules
> that would define the data clases for the resources.

#### Defining the Adapter

Once the `Resource` classes have been created, it is time to implement the `Adapter`
class by adding a new python module.

```shell
(myenv) $ vim adapter.py
```

Within this file it is required to create a class that should extend from
`ServiceResourceAdapter` of the `pyoslc_server.specification` package.

```python
import six
from pyoslc_server.specification import ServiceResourceAdapter

from pyoslc.vocabularies.rm import OSLC_RM
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

        if paging:
            offset = (page_no - 1) * page_size
            end = offset + page_size
            result = self.get_data(where)[offset:end]
        else:
            result = self.get_data(where)

        # This is just an example, the code could be improved
        if select:
            final_result = []
            sel = self.get_select(select)
            sel.append("http://purl.org/dc/terms/identifier")
            for r in result:
                final_result.append(self.select_attribute(r, sel))
        else:
            final_result = result

        return (
            len(self.items),
            final_result,
        )

    def get_select(self, select):
        result = []
        for p in select:
            if p.props:
                result += self.get_select(p.props)
            else:
                result.append(p.prop)

        return result

    def select_attribute(self, item, select):
        result = {}
        for k, v in six.iteritems(item):
            if k in select:
                result[k] = v
            else:
                if type(v) is dict:
                    value = self.select_attribute(v, select)
                    result[k] = value
                elif type(v) in (list, set):
                    lst = []
                    for i in v:
                        value = self.select_attribute(i, select)
                        lst.append(value)
                    result[k] = lst

        return result

    def get_data(self, where=None):
        result = list()
        for item in self.items:
            data = self.convert_data(item)
            result.append(data)

        return result

    def convert_data(self, item):
        return {
            "http://purl.org/dc/terms/identifier": item.identifier,
            "http://purl.org/dc/terms/description": item.description,
            "http://purl.org/dc/terms/title": item.title,
            "http://open-services.net/ns/rm#discipline": item.discipline,
            "http://purl.org/dc/terms/creator": {
                "http://purl.org/dc/terms/identifier": item.creator.identifier,
                "http://xmlns.com/foaf/0.1/firstName": item.creator.first_name,
                "http://xmlns.com/foaf/0.1/lastName": item.creator.last_name,
            },
        }
```

This class it is importing some modules and classes from the RDFLib and
from the vocabularies defined for the OSLC specification and that are defined
in the `pyoslc` package.

The OSLC resource type is assigned in the initialization of the adapter in
the `self.types` property, for the demo purpose it will be `Requirement` from
the `RM` specification.

A domain also was assigned to the class to be managed in the process of generating the
ServiceProvider

And finally the `query_capability` method is implemented and defines some parameters,
these parameters will be sent by the OSLC APP to the adapter to use them for the
query operation.

Keep in mind that the `Adapter` will be implemented by the developer who is 
creating or implementing the OSLC API, the `Adapter` will interact with the
data source, this means that the OSLC API is agnostic from the data store and 
the resources.

> Since this is an example, some methods of the Adapter are implemented
> just to fit the behavior required for the example, the implementation
> should be adjusted to fit the requirements of the datasource.

##### Attributes Mapping

Keep your eyes in the `convert_data` method within the `RequirementAdapter` class, 
this method is converting the python object into a dictionary but most important
the IDs of the attributes the IRI of the OSLC attribute.

On previous version of the SDK a dictionary was used to define the mapping of the 
OSLC attributes with the python object attribute.

This version delegate the responsibility of this to the implementer by using the OSLC IRI
of the attribute as the name of the attribute.


### Attaching the Adapter

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
(myenv) $ curl -X GET http://127.0.0.1:5000/oslc/services/catalog -H accept:"application/rdf+xml"
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

Now the ServiceProvider is listing the `RequirementAdapter`, let's see what is the
content of this endpoint by sending a request against its URL.

```bash
(myenv) $ curl -X GET http://127.0.0.1:5000/oslc/services/provider/adapter -H accept:"application/rdf+xml"
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

In the response of the ServiceProvider endpoint, there is `Service` tag that contains the
definition of a `QueryCapability` endpoint, this service is available here since the 
`query_capability` method was implemented in the `RequirementAdapter` class.

By overwriting the methods: `['query_capability', 'creation_factory', 'selection_dialog', 
'creation_dialog', 'get_resource']` from the `ServiceResourceAdapter` in any adapter class,
an endpoint will be added to the ServiceProvider.

The methods should be implemented (overwritten) by the developer as required, if 
the method is implemented, the OSL API will show the RDF representation for the
endpoint in the response.

Now, let's check what is the content of the `queryBase` endpoint of the OSLC API.

```bash
(myenv) $ curl -X GET http://127.0.0.1:5000/oslc/services/provider/adapter/resources -H accept:"application/rdf+xml"
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
datasource it is possible to use pagination for getting a specific number of 
resources. To use pagination, just add the `oslc.paging=true` to the query string 
to pass the parameter as defined in the specification.

By default, the pagination will return 50 resources per page, but it could be changed
by sending the `oslc.pageSize` parameter.

When the response uses pagination, it is possible to have different pages to complete
the response, thus the page number could be specified in the request.  

It is also possible to get specific attributes of the resources by using the `oslc.select`
in the query.

For more details you can see the [Query Syntax](https://archive.open-services.net/bin/view/Main/OSLCCoreSpecQuery)

For instance:

```bash
(myenv) $ curl -X GET http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.paging=true \
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
      </rdf:Description>
    </rdfs:member>
    <rdfs:member>
      <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/3">
        <dcterms:title>Capability to paging</dcterms:title>
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

There are some other options described in the [Query Syntax](https://archive.open-services.net/bin/view/Main/OSLCCoreSpecQuery)
specification, in which the `oslc.select` parameter could specify some other formats to
request some attributes from the resources even when this attributes come from nested
resources.

Here is an example:

```bash
(myenv) $ curl -G http://127.0.0.1:5000/oslc/services/provider/adapter/resources \
-d "oslc.paging=true" \
-d "oslc.pageSize=2" \
-d "oslc.pageNo=2" \
-d "oslc.prefix=foaf=<http://xmlns.com/foaf/0.1/>,oslc_rm=<http://open-services.net/ns/rm%23>,contact_plm=<https://contact-software.com/ontologies/v1.0/plm%23>" \
-d "oslc.select=dcterms:title,dcterms:creator{foaf:firstName},oslc_rm:discipline" \
-H accept:"application/rdf+xml"
```

Response:
```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:oslc="http://open-services.net/ns/core#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:oslc_rm="http://open-services.net/ns/rm#"
  xmlns:contact_plm="https://contact-software.com/ontologies/v1.0/plm#"
  xmlns:dcterms="http://purl.org/dc/terms/"
>
  <oslc:ResponseInfo rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.pageSize=2&amp;oslc.pageNo=2&amp;oslc.paging=true">
    <dcterms:title rdf:parseType="Literal">Query Results for Requirements</dcterms:title>
    <oslc:nextPage rdf:resource="http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.pageNo=3&amp;oslc.pageSize=2&amp;oslc.paging=true"/>
    <oslc:totalCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">5</oslc:totalCount>
  </oslc:ResponseInfo>
  <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources">
    <rdfs:member>
      <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/4">
        <oslc_rm:discipline rdf:parseType="Collection">
          <rdf:Description rdf:nodeID="Neb98cbf2a39541d383c9a283262a5768">
            <contact_plm:language>de</contact_plm:language>
            <contact_plm:text>Leistungsbedarf</contact_plm:text>
          </rdf:Description>
          <rdf:Description rdf:nodeID="Nf35ebf46fc0544f5ab1d028067b2aa1d">
            <contact_plm:text>Power Requirement</contact_plm:text>
            <contact_plm:language>en</contact_plm:language>
          </rdf:Description>
        </oslc_rm:discipline>
        <dcterms:creator rdf:resource="http://127.0.0.1:5000/oslc/services/provider/creator/resources/4"/>
        <dcterms:title>Capability to use select properties</dcterms:title>
      </rdf:Description>
    </rdfs:member>
    <rdfs:member>
      <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/adapter/resources/3">
        <dcterms:title>Capability to manage paging</dcterms:title>
        <dcterms:creator rdf:resource="http://127.0.0.1:5000/oslc/services/provider/creator/resources/3"/>
        <oslc_rm:discipline rdf:parseType="Collection">
          <rdf:Description rdf:nodeID="N59b8da4c291440e1aa33793555091acf">
            <contact_plm:text>Leistungsbedarf</contact_plm:text>
            <contact_plm:language>de</contact_plm:language>
          </rdf:Description>
          <rdf:Description rdf:nodeID="Nc00b504b85ab41dd8759ddb836656c07">
            <contact_plm:text>Power Requirement</contact_plm:text>
            <contact_plm:language>en</contact_plm:language>
          </rdf:Description>
        </oslc_rm:discipline>
      </rdf:Description>
    </rdfs:member>
  </rdf:Description>
  <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/creator/resources/4">
    <foaf:firstName>Arne</foaf:firstName>
  </rdf:Description>
  <rdf:Description rdf:about="http://127.0.0.1:5000/oslc/services/provider/creator/resources/3">
    <foaf:firstName>Christian</foaf:firstName>
  </rdf:Description>
</rdf:RDF>
```

In the above example, it is possible to see that the selection of the attributes 
could be specifying an attribute from the resource like `dcterms:title` or 
an attribute that comes inside a nested attribute like `dcterms:creator{foaf:firstName}`,
the different options that could be used for the selection are described in the 
[Query Syntax](https://archive.open-services.net/bin/view/Main/OSLCCoreSpecQuery)
specification

There is another section that could be mentioned in the response, it is the way 
that the attribute `oslc_rm:discipline` is described in the RDF representation.
The value for this attribute contains a list of resources and these are described
in a collection.


#### Requesting resources using where

It is also possible to get specific resources by using the `oslc.where`
in the query.

The next request shows how to use the `oslc.where` clause, but this is not
implemented in the `Adapter` example class, the idea is to implement the validation
and return the list of resources that fit the condition.

```bash
(myenv) $ curl -X GET http://127.0.0.1:5000/oslc/services/provider/adapter/resources?oslc.paging=true \
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