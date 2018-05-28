************
Interactions
************

Interaction is a recording of a request-response pair that is to be replayed during the test.


Scenarios
+++++++++

Scenarios are what interactions are organised into. For inspire-next they reside at::

   tests/e2e/scenarios

The directory structure is as follows::

   scenarios/<scenario_name>/<service_name>/<interaction>.yaml

Scenario name can be anything,
but by convention it is the name of the E2E test. Service name has to match one of the services
defined in :attr:`inspire_mitmproxy.services`. Name of the interaction can be anything, and is only
for informative purposes.


Structure of interactions
+++++++++++++++++++++++++

.. code-block:: yaml

    request:
      body: 'Body of the request'           # string (or bytes)
      headers:
        Content-Type: ['text/plain']        # array of strings ()
        Host: ['samplehost.local']
      method: 'PUT'                         # string
      url: 'http://samplehost.local/path'   # string
    response:
      body: 'Body of the response'          # string (or bytes)
      headers:
        Content-Type: ['text/plain']        # array of strings
      status:
        code: 200                           # integer
        message: OK                         # string
    match:
      exact:
      - method                              # array of one of the keys in request
      - uri
      regex:
        method: 'PUT|POST'                  # dict with keys of the keys in request
    callbacks:
    - delay: 10                             # integer (seconds)
      request: {}                           # follows request as above


Matching
++++++++

By default the request is matching the prerecoded request if their urls, methods and bodies are
equal. You can specify custom matching rules per interaction by using the `match` field in the
interaction YAML file. There are two types of matchings:

- **exact**: the field specified matches exactly
- **regex**: the field specified (as key in the dictionary) matches the regex defined in value
