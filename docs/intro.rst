************
Introduction
************

INSPIRE-MITMProxy is a solution for running E2E tests in INSPIRE. It intercepts all HTTP(S) traffic
from the workers (web, task and crawler nodes) and either let's it pass through (e.g. when
communication happens with internal services) or parses the incoming request and replies according
to predefined (recorded) responses.


Dispatcher
++++++++++

Dispatcher is the object which decides which service is responsible for handling an incoming
request: all of the services are registered with the dispatcher. When a new request comes, the
dispatcher iterates through the services until it either finds one that handles the request (by
using :meth:`~inspire_mitmproxy.services.base_service.BaseService.handles_request`, or fails with
HTTP 501: :exc:`~inspire_mitmproxy.errors.DoNotIntercept`.


Services
++++++++

Service is a basic building block of inspire-mitmproxy: each service imitates one of the external
services we are mocking. In the basic case it has defined hostnames on which it listens, and if
a request is matching one of those, it is passed to the service using
:meth:`~inspire_mitmproxy.services.base_service.BaseService.process_request`.


Management Service
++++++++++++++++++

:class:`~inspire_mitmproxy.services.management_service.ManagementService` is aware of the other
services and is used to orchestrate tests. Tests are organised in scenarios. In order to set a test
scenario, a POST or PUT request has to be sent to its `/config` endpoint, like:

.. code-block:: json

   {
      "active_scenario": "name of scenario"
   }

When the mitmproxy starts, the active scenario is `default`: since a scenario can be set only at
the beginning of a test, this is to ensure that all of the responses required for proper start-up
of INSPIRE are present.
