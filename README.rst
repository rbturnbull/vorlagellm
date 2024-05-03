================================================================
VorlageLLM
================================================================

.. start-badges

|testing badge| |coverage badge| |docs badge| |black badge| |torchapp badge|

.. |testing badge| image:: https://github.com/rbturnbull/vorlagellm/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/rbturnbull/vorlagellm/actions

.. |docs badge| image:: https://github.com/rbturnbull/vorlagellm/actions/workflows/docs.yml/badge.svg
    :target: https://rbturnbull.github.io/vorlagellm
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/132c627e616e59fa78f663e4a4ff6f0f/raw/coverage-badge.json
    :target: https://rbturnbull.github.io/vorlagellm/coverage/

.. |torchapp badge| image:: https://img.shields.io/badge/MLOpps-torchapp-B1230A.svg
    :target: https://rbturnbull.github.io/torchapp/
    
.. end-badges

.. start-quickstart

Uses an LLM to determine which were plausible readings in the Vorlage of a translation of a text.

Installation
==================================

Install using pip:

.. code-block:: bash

    pip install git+https://github.com/rbturnbull/vorlagellm.git


Usage
==================================

See the options for training a model with the command:

.. code-block:: bash

    vorlagellm train --help

See the options for making inferences with the command:

.. code-block:: bash

    vorlagellm infer --help

.. end-quickstart


Credits
==================================

.. start-credits

Robert Turnbull
For more information contact: <robert.turnbull@example.com>

Created using torchapp (https://github.com/rbturnbull/torchapp).

.. end-credits

