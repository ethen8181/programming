
# Web Service

## Basic Definition of Web Service

Software system designed to support interoperable application-to-application interaction over a network.

- application-to-application. e.g. A web application that renders html to a human user would not be considered a web service as it is meant for application-human interaction.
- It should be interoperable such as it is not platform dependent. i.e. irrespective of the technology that the other application is built upon, they should be able to talk to our web application.
- Should allow communication over the network. e.g. if we package our business logic inside a JAR file, then that JAR file is embedded locally and that communication would not fall into the bucket of "over the network".

## Hows of Web Service

**How does data exchange between applications take place:** A web application talks to another web application by sending a request, asking for the piece of information that we're interested in. In return, the web application that receives the request will process that request and potentially sends back a reponse.

**How can we make web services platform independent:** For a web application to be platform independent, the message exchange format of the request and response should also be technology-agnostic. e.g. popular options are XML, JSON.

**How does the application know the format of the request and response:** To allow other web application to talk to us, we as a web service need to have some sort of service definition. The would specify request/reponse format (e.g. XML, JSON), structure (what would the input and output data contain) and the endpoint (where is the service available, do we talk to the service using HTTP or Message Queues).

## Type of Web Service

There're two major ways of building web services:

**SOAP (Simple Object Access Protocol):**

- We use XML as the exchange format. The request and response is based on a specific XML structure. Namely, we need to create a SOAP envelope that contains a header and body.
- It poses no restriction on the way we transport the data. i.e. It we can HTTP or Message Queues.
- The service definition is usually done by WSDL (Web Service Definition Language).

**REST (Representational State Transfer):**

The idea is to make best use of HTTP (Hyper Text Transfer Protocol). Common terminologies that we'll encounter are HTTP Methods (GET - we're trying get something back. PUT, we're trying to update something. POST - we're trying to create something) and HTTP status codes (200 - successful, 404 - web not page).

One of key abstraction is a Resource. For every Resource, we would define its corresponding URI (Uniform Resource Identifier). e.g. If we would like to get some information about the user, we can get it with `/user/[name of the user we're interested in]`.

- There're no restrictions in the data exchange format. Although JSON is an extremely popular choice.
- The transport is always HTTP.
- There're no standard for service definition. Common options are Swagger.









