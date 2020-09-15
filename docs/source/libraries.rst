===============
Libraries used.
===============

In the development of the **PyOSLC** project there were different libraries used 
for different goals or to cover specific requirements.

All these libraries meet a specific objective in the project but there are 
some of them that need to be described.

Flask and extensions.
=====================
Since **PyOSLC** will be used to deploy web services, Flask was selected to create 
the web application and some other extensions were used to extend the web 
application as a REST-based API which is also able to manage templates, forms, 
logins, and databases for manipulating different type or requests and data.

RDFLib and serializers.
=======================
Another main library to mention is RDFLib which allows the manipulation of 
the input and output using the RDF standard model which is part of the 
OSLC specification. The RDFLib was also extended by using other plugins 
to implement serializers to convert the output in different formats.

Authlib for OAuth.
=======================
There is also a third component that was used to implement the authentication 
process and to enable the OAuth workflow required for the integration of an 
OSLC API with other applications.
