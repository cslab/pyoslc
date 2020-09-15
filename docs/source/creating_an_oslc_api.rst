Creating an OSLC API using PyOSLC.
##################################
The main goal of the PyOSLC SDK is to use the set of classes and libraries 
for the implementation or development of an OSLC API, to achieve this goal 
it is necessary to work or add the SDK over an existent Flask web app.

Creating the Flask application.
===============================
The first step to create an OSLC API where using the PyOSLC SDK is to have 
or create a Flask application, this is not a tutorial to show how to create 
a Flask application, it assumes that there is a Flask application created.

This is an example of a Flask application using the factory pattern.

.. code-block:: python

    from flask import Flask

    def create_app(app_config=None):
        app = Flask(__name__)
        app.config.from_object(app_config)

        return app

This code is the minimum required to create a web app using flask. Here the 
app variable represents an instance of the Flask class which creates the web 
application and it can be used to execute the web app.

Adding the OSLC module.
=======================
As mentioned in the beginning of this document, in addition to Flask, 
the PyOSLC SDK is also developed using Flask-RESTx which is an extension 
of Flask for extending the web app into a REST-based web service.

The Flask microframework has a tool called Blueprint that helps to organize 
the application using or segmenting the paths of the endpoints or urls, 
in the case of Flask-RESTx it is possible to use another concept called 
Namespace that allows to organize the application.

Within the PyOSLC SDK there is a module that uses a Blueprint and a Namespace 
for implementing the endpoints for the OSLC API, then to add this module 
into the Flask application it should be imported and initialized using the 
following lines.

.. code-block: python

    def create_app(app_config=None):
        app = Flask(__name__, instance_relative_config=False)
        app.config.from_object(app_config)

        from app.api.adapter import oslc
        oslc.init_app(app)

        return app

The new lines are importing the `oslc` module from the api.adapter package, 
this module represents the OSLC API, and the call to the method ``init_app`` 
it is required to add the `oslc` module to the `app` object which is the 
flask application as mentioned.

The initialization of the oslc module is implemented by registering the 
oslc blueprint instance to the flask application with a prefix (oslc for 
instance) and by adding the adapter instance as a namespace to an api object, 
these elements will be explained later..

.. code-block:: python

    from app.api.adapter import bp, api
    from app.api.adapter.namespaces.core import adapter_ns

    def init_app(app):
        app.register_blueprint(bp, url_prefix='/oslc')
        api.add_namespace(adapter_ns)

The OSLC blueprint and Api.
---------------------------
The first step in the initialization process is to register the blueprint 
instance to the flask application, a blueprint is a way to organize a web 
app in Flask and this allows a developer to create specific paths for a set 
of endpoints.

The second step in the initialization is to add a namespace object to the 
api instance. This addition is required to define the classes that implement 
the endpoints for the API. 

Here is the definition of these two objects, the blueprint has different 
parameters but in this case the url_prefix will be used as part of the 
endpoints and it will be added to the prefix used in the registration. 
The Api object defines the Swagger specification for the API and will be 
used for the auto documented web app.

.. code-block:: python

    from flask import Blueprint
    from flask_restx import Api

    bp = Blueprint('oslc', __name__, url_prefix='/services', static_folder='static')

    api = Api(
        app=bp,
        version='1.0.0',
        title='Python OSLC API',
        description='Implementation for the OSLC specification for python application',
        contact='Contact Software & Koneksys',
        contact_url='https://www.contact-software.com/en/',
        contact_email="oslc@contact-software.com",
        validate=True
    )


The Adapter namespace.
----------------------
The adapter namespace defines and implements all the methods for managing 
the requests to the OSLC API through the usage of the “Resource” class which 
is a class from Flask-RESTx extension that manages the methods like GET, 
POST, PUT, DELETE.

The definition of a Namespace allows to organize and to structure the endpoints 
by specific objectives. In the case of the PyOSLC demo, the adapter namespace 
defines the endpoints for the ServiceProviders of the OSLC API.

Here are some examples of endpoints.

.. code-block:: python

    from flask_restx import Namespace, Resource

    adapter_ns = Namespace(name='adapter', 
                           description='Python OSLC Adapter', 
                           path='/services',)

    class OslcResource(Resource):
        ...

    @adapter_ns.route('/catalog')
    class ServiceProviderCatalog(OslcResource):
        ...

    @adapter_ns.route('/provider/<service_provider_id>')
    class ServiceProvider(OslcResource):
        ...

    @adapter_ns.route('/provider/<service_provider_id>/resources/requirement')
    class ResourceOperation(OslcResource):
        ...

    @adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>')
    class ResourcePreview(OslcResource):
        ...

    @adapter_ns.route('/rootservices')
    class RootServices(OslcResource):
        ...


Service Provider Catalog.
-------------------------
The entry point of an OSLC API is the Service Provider Catalog instance. 
The implementation of this service will allow the discoverability of the 
services exposed by the OSLC API for a domain specific application.

Using the PyOSLC SDK it is possible to create a class which will assign all 
the required values to expose the information defined for the domain specific 
application.

There are also other classes and components that allow the creation and 
configuration of the ServiceProviderCatalog to have the better format of the 
ServiceProviderCatalog response depending on the application that should be 
exposed.

ServiceProviderCatalogSingleton class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The goal of this class is to initialize the elements for a specific project, 
and it will initialize all the components for the project such as the 
ServiceProviderCatalog, the ServiceProvider’s, Services including QueryCapability, 
CreationFactory and so on.

Here is an example of the signatures of some methods of this class.

.. code-block:: python

    from app.api.adapter.manager import CSVImplementation
    from app.api.adapter.services.factories import ContactServiceProviderFactory
    from pyoslc.resources.models import ServiceProviderCatalog,

    class ServiceProviderCatalogSingleton(object):

        def __new__(cls, *args, **kwargs):
            if not cls.instance:
                ...
                cls.catalog = ServiceProviderCatalog()
                ...
            return cls.instance


        @classmethod
        def get_catalog(cls, catalog_url):
            ...
            cls.initialize_providers(catalog_url)
            return cls.catalog

        @classmethod
        def initialize_providers(cls, catalog_url):

            service_providers = CSVImplementation.get_service_provider_info()

            for sp in service_providers:
                identifier = sp.get('id')
                if identifier not in cls.providers.keys():
                    ...
                    sp = ContactServiceProviderFactory.create_service_provider(catalog_url, title, description, publisher, parameters)
                    ...

            return cls.providers

        @classmethod
        def register_service_provider(cls, sp_uri, identifier, provider):
            ...

        @classmethod
        def construct_service_provider_uri(cls, identifier):
            ...

        @classmethod
        def get_domains(cls, provider):
            ...

The main part of this example code is the ``__new__`` method and the 
instantiation of the ServiceProviderCatalog class. This means that the 
catalog object is created using the class imported from the model package 
and it creates an object with the definition for the ServiceProviderCatalog 
resource with all the attributes defined in the OSLC specification.

.. code-block:: python

    class ServiceProviderCatalog(BaseResource):

        def __init__(self, about=None, types=None, properties=None, description=None,
                        identifier=None, short_title=None, title=None, contributor=None,
                        creator=None, subject=None, created=None, modified=None, type=None,
                        discussed_by=None, instance_shape=None, service_provider=None,
                        relation=None, uri=None, publisher=None, domain=None,
                        service_provider_catalog=None, oauth_configuration=None):
            ...


        def to_rdf(self, graph):
            ...

The ServiceProviderCatalog class also has another method called to_rdf() 
which will be described later.

As shown in the ServiceProviderCatalogSingleton code there are some methods 
that should be used to initialize the services depending on a “CSVImplementation” 
class, this class defines the list of service providers that should be 
exposed by the OSLC API. In this case it refers to CSV implementation which 
means that the information will come from a CSV file.

Here is an example of this class.

.. code-block:: python

    from app.api.adapter.services.specification import Specification

    class CSVImplementation(object):

        @classmethod
        def get_service_provider_info(cls):
            service_providers = [{
                'id': 'Project-1',
                'name': 'PyOSLC Service Provider for Project 1',
                'class': Specification
            }]

            return service_providers

The shown example defines the attributes for the service provider, an `id`, 
a `name` that will be used as the title of the service provider and 
the name of a `class` that defines the elements that could be exposed by 
the OSLC API in this case the class is called “Specification”.

The Specification class is also a definition for the resources that should be 
exposed through the OSLC API and more specifically the information of 
the Query Capability, Creation Factory and Dialogs.

.. code-block:: python

    class Specification(ServiceResource):
        
        domain = 'http://open-services.net/ns/rm#'
        service_path = 'provider/{id}/resources'

        @staticmethod
        def query_capability():
            return {
                'title': 'Query Capability',
                'label': 'Query Capability',
                'resource_shape': 'resourceShapes/requirement',
                'resource_type': ['http://open-services.net/ns/rm#Requirement'],
                'usages': []
            }

        @staticmethod
        def creation_factory():
            ...

        @staticmethod
        def selection_dialog():
            ...

        @staticmethod
        def creation_dialog():
            ...

In this code some methods were defined to specify the value or data for 
the services that will be added or assigned to a service provider, 
it also defines the domain and the path of these services in the OSLC API.

All the shown code in these examples could be hardcoded or retrieved from 
an external application but should meet this structure to be able to take 
the information for creating the components.

ServiceProviderFactory class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Beside of the ServiceProviderCatalogSingleton class and the other classes 
required for getting the information or definition of the Service Providers, 
there is another class that is important to mention, the ContactServiceProviderFactory, 
which is used in the initialization of the service providers, but this class is 
only an implementation for calling to the ServiceProviderFactory class 
which is in charge of doing the magic for creating the services and all the 
configurations.

An example of the method’s signatures of the ServiceProviderFactory class 
are shown here.

.. code-block:: python

    from pyoslc.resources.models import ServiceProvider, Service, QueryCapability, CreationFactory, Dialog

    class ServiceProviderFactory(object):

        @classmethod
        def create_service_provider(cls, base_uri, title, description, 
                                    publisher, resource_classes, parameters):
            return cls.initialize(ServiceProvider(), base_uri, title, description, 
                                  publisher, resource_classes, parameters)

        @classmethod
        def initialize(cls, service_provider, base_uri, title, description, 
                       publisher, resource_classes, parameters):
            ...                       

        @classmethod
        def create_query_capability(cls, base_uri, attributes, parameters):
            ...

        @classmethod
        def creation_factory(cls, base_uri, attributes, parameters, class_path, method_path):
            ...

        @classmethod
        def create_selection_dialog(cls, base_uri, attributes, parameters):
            ...

        @classmethod
        def create_creation_dialog(cls, base_uri, attributes, parameters):
            ...

This class is responsible to create the instance for the ServiceProvider, 
and is created within the `create_service_provider` method using the 
ServiceProvider class, which is also defined within the ``model`` package 
and has all the attributes defined for a `ServiceProvider` as described 
in the OSLC specification.

.. code-block:: python

    class ServiceProvider(BaseResource):

        def __init__(self, about=None, types=None, properties=None, 
                    description=None, identifier=None, short_title=None, 
                    title=None, contributor=None, creator=None, subject=None, 
                    created=None, modified=None, type=None, discussed_by=None, 
                    instance_shape=None, service_provider=None, relation=None, 
                    publisher=None, service=None, details=None, 
                    prefix_definition=None, oauth_configuration=None):
            ...

The ServiceProviderFactory class also has the methods to create the services 
like `QueryCapability`, `CreationFactory` and the other services that should 
be exposed through the OSLC API, in the code shown above there are other 
methods implemented for other services.

An example of the implementation for creating a `QueryCapability` is shown 
below.

.. code-block:: python

    @classmethod
    def create_query_capability(cls, base_uri, attributes, parameters):
        title = attributes.get('title', 'OSLC Query Capability')
        label = attributes.get('label', 'Query Capability Service')
        resource_shape = attributes.get('resource_shape', '')
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        base_path = base_uri + '/'
        class_path = 'provider/{id}/resources'
        method_path = 'requirement'

        base_path = base_path.replace('/catalog', '')

        query = cls.resolve_path_parameter(base_path, class_path, method_path, parameters)

        query_capability = QueryCapability(about=query, title=title, query_base=query)
        if label:
            query_capability.label = label

        if resource_shape:
            resource_shape_url = urlparse(base_path + resource_shape)
            query_capability.resource_shape = resource_shape_url.geturl()

        for rt in resource_type:
            query_capability.add_resource_type(rt)

        for u in usages:
            query_capability.add_usage(u)

        return query_capability

In this example, it is important to put attention in the creation of the 
`QueryCapability` object, which is an instance of the `QueryCapability` class 
and as the previous classes mentioned so far, it is defined in the same 
package and it also meets the OSLC specification on its attributes.

.. code-block:: python

    class QueryCapability(BaseResource):

        def __init__(self, about=None, types=None, properties=None, 
                    description=None, identifier=None, short_title=None,
                    title=None, contributor=None, creator=None, subject=None, 
                    created=None, modified=None, type=None, discussed_by=None,
                    instance_shape=None, service_provider=None, relation=None,
                    label=None, query_base=None, usage=None, resource_type=None,
                    resource_shape=None):
            ...

The implementation of all these components are based on the instantiation 
of the objects with the classes defined in the PyOSLC SDK defined within 
the package pyoslc.resource.models.

ServiceProvider per Project.
----------------------------
For each project that the OSLC API should expose there should be 
a set of endpoints that will be implemented for the operation of 
the requests to retrieve, create, update or address whichever 
operation over the resources.

There is a class that is called on each of these requests to attend 
the request and to process the operation and return response.

.. code-block:: python

    adapter_ns.route('/provider/<service_provider_id>/resources/requirement')
    class ResourceOperation(OslcResource):
        ...

This class has the methods for these operations, and on each request 
it processes the information to send the response to the client 
for each request.

Generating RDF Responses.
-------------------------
An OSLC API should meet the set of endpoints to have access to the 
information through the different ServiceProviders and services, but one 
of the most important parts of an OSLC API is the representation or 
the format of the information exchanged between the client and the server.

The standard format for exchanging information through an OSLC API is RDF 
and for doing this within the PyOSLC SDK the RDFLib is used for serializing 
the information.

Within the methods of the OSLC adapter the information is managed in 
a python objects, but when a data is received in RDF format or should be sent 
to the client in RDF format the RDFLib is used to transform the information 
from python objects into a Graph and then transformed into an RDF representation 
using whichever of the known formats: application/rdf+xml, text/turtle, 
and even within the PyOSLC SDK a plugin for the RDFLib is used to convert 
the information into the application/ld+json format.

Within the OslcResource class which is a base class that extends from 
the Resource class of Flask-RESTx there is implemented a method called 
create_response, which is responsible to take the information generated 
with the OSLC Resource classes (serviceprovider, querycapability and so on) 
and to convert the information within each class into a RDF representation.

Here is a section of the code of the create_response method, that shows 
the serialization of the OSLC resource into a graph and then into 
the response.

.. code-block:: python

    class OslcResource(Resource):

        def __init__(self, *args, **kwargs):
            super(OslcResource, self).__init__(*args, **kwargs)

            self.graph = kwargs.get('graph', Graph())
            self.graph.bind('oslc', OSLC)
            self.graph.bind('rdf', RDF)
            self.graph.bind('rdfs', RDFS)
            self.graph.bind('dcterms', DCTERMS)
            self.graph.bind('j.0', JAZZ_PROCESS)

        @staticmethod
        def create_response(graph, accept=None, content=None, rdf_format=None, etag=False):

            accept = accept if accept is not None else request.headers.get('accept', 'application/rdf+xml')

            content = content if content is not None else request.headers.get('content-type', accept)
            if content.__contains__('x-www-form-urlencoded'):
                content = accept

            rdf_format = accept if rdf_format is None else rdf_format

            if accept in ('application/json-ld', 'application/ld+json', 'application/json', '*/*'):
                # If the content-type is any kind of json,
                # we will use the json-ld format for the response.
                rdf_format = 'json-ld'

            if rdf_format in ('application/xml', 'application/rdf+xml'):
                rdf_format = 'pretty-xml'

            if rdf_format.__contains__('rootservices-xml') and (not accept.__contains__('xml')):
                rdf_format = accept

            if rdf_format == 'application/atom+xml':
                rdf_format = 'pretty-xml'

            data = graph.serialize(format=rdf_format)

            # Sending the response to the client
            response = make_response(data.decode('utf-8'), 200)
            response.headers['Accept'] = accept
            response.headers['Content-Type'] = content
            response.headers['OSLC-Core-Version'] = "2.0"

            if etag:
                response.add_etag()

            return response

In this code it is shown how the information that comes as a RDF Graph is 
serialized into a specific format defined by the rdf_format variable, 
the serializers will be explained later.

The serialized data is also used to generate the Response object that 
will be sent to the client, this response object it is also performed 
adding other elements in the header section to specify the ``Accept``, 
``Content-Type`` values to specify the format of the serialization, 
there is also another header that specifies the version of the 
OSLC specification used.

RDF Serializers.
----------------
In the previous section was explained how the data that should be sent 
to the client is transformed from a python object which is represented 
as a Graph into a string that contains the information with an specific 
RDF format, this format will depend on the serializer used in the format 
parameter of the serializer method.

The RDFLib library comes with some serializers by default, but it is possible 
to extend this to add or modify a serializer, the default is the XML Serializer, 
which convert the graph into a RDF using the application/rdf+xml format, 
there is also a Turtle Serializer which converts the graph into a turtle 
format.

The PyOSLC has its own serializer called JazzRootServiceSerializer, 
this is a serializer used for generating an specific RDF representation 
for integrating the PyOSLC API with a Jazz application, this process 
will be explained later in the document.


RDF Namespaces.
---------------
Namespaces and vocabularies are other important elements when talking 
about RDF, it is known that when writing RDF it is necessary to establish 
the Namespaces and the vocabulary used in the representation of a resource.

There are different namespaces depending on the domain of the application 
or the project. PyOSLC has defined the Namespaces required for the 
implementation of the OSLC specification and to have the availability 
of the namespaces for the most common domains like RM, QM and so on.

The definition of these namespaces are in the package ``pyoslc.vocabularies`` 
and there is a list of modules defining all these namespaces.


Adding the OSLC OAuth module.
=============================
The PyOSLC SDK includes a module that enables the Authentication and 
Authorization in a OSLC API, this module allows the capability to protect 
the requests against the endpoints or to add a security layer when working 
in an integration with an external application such as Jazz (this will be 
explained later).

The OSLC OAuth could be added into the Flask web app as an independent 
module.

.. code-block:: python

    def create_app(app_config=None):
        app = Flask(__name__, instance_relative_config=False)
        app.config.from_object(app_config)

        from app.api.adapter import oslc
        oslc.init_app(app)
        
        from app.api.oauth import oslc_oauth
        oslc_oauth.init_app(app)

        return app

As shown previously with the configuration of the oslc module, 
the oslc_oauth module requires to be initialized to configure all 
the elements required for managing the security.

Here is the code that shows the initialization of the oslc_oauth module.

.. code-block:: python

    import pyoslc_oauth
    from app.api.oauth.pyoslc_app import PyOSLCApplication

    pyoslc = PyOSLCApplication('PyOSLC Contact Software')

    def init_app(app):
        pyoslc_oauth.init_app(app, pyoslc)

In the previous code there is a PyOSLCApplication class that is imported 
and then instantiated, this is only an implementation of the OAuthApplication 
class which is managed as an interface (in Python there is no interfaces 
implemented but this class simulates an interface) and should implements 
some methods that will validate the user and permissions.

The code of the demo application is shown here:

.. code-block:: python

    from flask import request
    from flask_login import login_user

    from pyoslc_oauth import OAuthApplication
    from pyoslc_oauth.models import User
    from pyoslc_oauth.resources import OAuthException


    class PyOSLCApplication(OAuthApplication):
        """
        This application was implemented for managing the
        authentication of the adapter, it extends the
        OAuthApplication from pyoslc to meet the implementation
        of the pyoslc authentication process.
        """

        def get_realm(self):
            pass

        def is_authenticated(self):
            pass

        def login(self, username, password):
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                raise OAuthException('Email or password is invalid.')

            login_user(user)

        def is_admin_session(self):
            return request.args.get('admin')

The method called login in this implementation is the most important part, 
and it uses classes from other Flask extensions such as Flask-Login, 
this method validate the username and password against a database and 
if the user exists and the credentials are correct, the ``login_user`` 
method from the Flask-Login extension is used to set the information 
of the user into the session.

Resuming the initialization of the oslc_oauth module, there is also another 
important element that should be explained, the pyoslc_oauth module. 
This module contains the objects and instances from the OAuthlib which is 
used to implement the OAuth workflow for the PyOSLC SDK.

This is the code 

.. code-block:: python
    
    import os

    from flask_bootstrap import Bootstrap
    from pyoslc_oauth import database, server
    from pyoslc_oauth.login_manager import login
    from pyoslc_oauth.resources import OAuthConfiguration, FileSystemConsumerStore, OAuthApplication, OSLCOAuthConsumer
    from pyoslc_oauth.routes.consumer import consumer_bp
    from pyoslc_oauth.routes.oauth import oauth_bp

    base_dir = os.path.abspath(os.path.dirname(__file__))


    oauth_config = OAuthConfiguration()
    file_consumer = FileSystemConsumerStore(os.path.join(base_dir, 'OAuthStore.rdf'))
    oauth_app = OAuthApplication('PyOLSC')
    client = OSLCOAuthConsumer()


    def init_app(app, oslc_oauth_app=None):
        database.init_app(app)
        login.init_app(app)
        oauth_config.consumer_store = file_consumer
        oauth_config.application = oslc_oauth_app or oauth_app
        app.register_blueprint(oauth_bp)
        app.register_blueprint(consumer_bp)
        Bootstrap(app)
        server.init_app(app)

There are different elements here, but the elements that should be mentioned 
as part of the OAuth implementation for now (the other will be explained 
later) are the oauth_bp which is the blueprint that implements the endpoints 
for the generation of the tokens and consumer_bp which is another set of 
endpoints for managing the information of the consumers. 

Adding integration with JAZZ.
=============================
Once PyOSLC is used to implement or develop an OSLC API it would be 
necessary to start an integration of the OSLC API with an external 
application such as DNG, RQM from the IBM JAZZ set of tools.

If this is the case, PyOSLC SDK has implemented some services and 
classes to achieve this integration.

It is necessary to keep in mind that JAZZ has some specific requirements 
to achieve the integrations, and PyOSLC tried to cover all these 
requirements.

RootServices.
-------------
The entry point to start an integration with a JAZZ application is to have 
a endpoint within the OSLC API that should return an RDF document with some 
specific components, this document is required by a specification 
established by IBM JAZZ and is called rootservices.

In the PyOSLC SDK there is a resource class called Rootservices that allows 
the generation of this document. In the OSLC API demo application there is 
also an endpoint that has been implemented to return the RDF document 
required.

Here is a section of the code:

.. code-block:: python

    @adapter_ns.route('/rootservices')
    class RootServices(OslcResource):

        def get(self):

            """
            Generate Rootservices response
            """
            endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
            base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

            rootservices_url = urlparse(base_url).geturl()

            root_services = RootServiceSingleton.get_root_service(rootservices_url)
            root_services.about = request.base_url
            publisher_url = rootservices_url.replace('rootservices', 'publisher')
            root_services.publisher = PublisherSingleton.get_publisher(publisher_url)
            root_services.to_rdf(self.graph)

            return self.create_response(graph=self.graph, rdf_format='rootservices-xml')

Since the rootservice document is a specification from IBM JAZZ it requires 
a particular structure of the RDF, then it was necessary to implement 
a serializer to generate the RDF with the required structure, this serializer 
was stored in the pyoslc.serializer package and is the module is called ``jazzxml``, 
the name of the rdf_format for the serialization is ``rootservices-xml`` 
as shown in the call of th create_response method.

Within the RDF response generated by this endpoint there is a particular 
section where the endpoints for the authentication and authorization 
are listed, these endpoints represent the OAuth workflow that should be 
followed by JAZZ and the PyOSLC to achieve the integration.

The Other main section of the rootservice document is the description 
of the ServiceProviderCatalog and all the services exposed by the PyOSLC 
that could be accessed by the JAZZ application in the integration process.

Adding PyOSLC as a Friend.
--------------------------
Within the process of the integration of PyOSLC API and the JAZZ application 
there is a step where the JAZZ application should be added within the OSLC API 
as a consumer, this process is called Friend in the JAZZ side.

To achieve the consumer or friend it is required to have two sets of endpoints 
within the oslc_oauth module described previously.

The ``oauth_bp`` is the set of endpoints required to manage the request 
to generate and validate the tokens of a client that wants to access 
the endpoint in the PyOSLC API.

.. code-block:: python

    oauth_bp = Blueprint('oauth', __name__, template_folder='../templates', static_folder='../static')

    @oauth_bp.route('/initiate', methods=['POST'])
    def initiate_temporary_credential():
        ...
    
    @oauth_bp.route('/authorize', methods=['GET', 'POST'])
    def authorize():
        ...

    @oauth_bp.route('/token', methods=['POST'])
    def issue_token():
        ...

On the other side, there is another set of endpoints called ``consumer_bp``, 
this endpoints have the responsibility to register the JAZZ application 
within the PyOSLC by generating a client id and the other elements that 
should be validated in the JAZZ side.

Here is a section of code of the ``consumer_bp``.

.. code-block:: python

    consumer_bp = Blueprint('consumer', __name__)

    @consumer_bp.route('/')
    def get_consumers():
        ...

    @consumer_bp.route('/register', methods=['POST'])
    def register():
        ...

    @consumer_bp.route('/approve', methods=['GET', 'POST'])
    def approve():
        ...

    @consumer_bp.route('/approve/<key>', methods=['GET', 'POST'])
    @login_required
    def authorized(key):
        ...

    @consumer_bp.route('/admin', methods=['GET'])
    def show_consumer_key_management():
        ...

    @consumer_bp.route('/adminLogin', methods=['POST'])
    def admin_login():
        ...

These are only the signatures of the methods used for the endpoints.

Once the process of generating the client and secrets in the PyOSLC side 
and the Friend in the JAZZ application side have finished, it is possible 
to start working with these applications.

Creating associations.
----------------------
When a JAZZ application or an OSLC API wants to interact with each other 
to share information it is necessary to establish an integration and 
to create associations between these projects to be able to access 
the information from one to the other.

The previous step is required, the friendship or consumer, once this 
has been achieved is required to create associations from a specific domain 
application of JAZZ such as DNG or RQM to the OSLC API.

In the creation of this association will start an interaction between 
the JAZZ application and the PyOSLC, the endpoints and responses 
for managing this interaction are implemented in the demo application.
