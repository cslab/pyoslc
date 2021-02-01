Getting the code.
=================
PyOSLC is available as an open-source project and it could be accessed 
through its git repository in the next url.

ssh: git@gitlab.contact.de:frank/pyoslc.git

https: https://gitlab.contact.de/frank/pyoslc.git

It is possible to clone the project using a git client (desktop or command line).

Knowing the project.
--------------------
After cloning the project there are some important points to know about 
the structure and architecture of the project.

Let’s see the structure of the project:

::

    $ tree pysolc
    ├── .env
    ├── .flaskenv
    ├── LICENSE
    ├── MANIFEST.in
    ├── README.md
    ├── app
    ├── examples
    ├── initialize.py
    ├── pyoslc
    ├── pyoslc_oauth
    ├── requirements.txt
    ├── setup.cfg
    └── setup.py

The structure of the project shows some files and folders that contain 
the implementation of the SDK and an example of how to use it for creating 
an OSLC API.

The pyoslc folder.
^^^^^^^^^^^^^^^^^^
This folder contains the classes that define the SDK, classes to create 
the instances for ServiceProvider, Service, QueryCapability and the other 
components for an OSLC API.

The pysocl_oauth folder.
^^^^^^^^^^^^^^^^^^^^^^^^
This folder contains the classes and the implementation of the authentication 
and the authorization process to an OSLC API, it also includes the implementation 
of the OAuth workflow required for other OSLC API which PyOSLC could interact with.

The app folder.
^^^^^^^^^^^^^^^
This is the implementation of the PyOSLC SDK, is an example of how to use 
or implement the PyOSLC SDK for creating an OSLC API, contains the implementation 
of the REST-based API and all the services for exposing the information 
using the SDK.
