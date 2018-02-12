Sphinx SATySFi builder
=============================

Sphinx to SATySFi builder.

Note: This is just a trial builder. It will NOT publish to pypi and not implement all of SATySFi features.

Satysfi: https://github.com/gfngfn/SATySFi

Setting
=======

Install
-------

::

   % pip install -e "git+https://github.com/shirou/sphinxcontrib-satysfibuilder#egg=sphinxcontrib_satysfibuilder"



Configure Sphinx
----------------

To enable this extension, add ``sphinxcontrib.satysfibuilder`` module to extensions
option at `conf.py`.

::

   # Enabled extensions
   extensions = ['sphinxcontrib.satysfibuilder']

   # Add title, author information
   satisfy_documents = [
       (master_doc, 'SATySFi.saty', 'SATySFi Builder', 'shirou'),
   ]


How to use
=====================

::

  % make satysfi


Repository
==========

https://github.com/shirou/sphinxcontrib-satysfibuilder

Sample
-------



License
========

LGPL v3.

Same as SATySFi original. See LICENSE file.
