Sphinx SATySFi builder
=============================

.. image:: https://badge.fury.io/py/sphinxcontrib-satysfibuilder.svg
    :target: https://badge.fury.io/py/sphinxcontrib-satysfibuilder

.. image:: https://circleci.com/gh/shirou/sphinxcontrib-satysfibuilder.svg?style=svg
    :target: https://circleci.com/gh/shirou/sphinxcontrib-satysfibuilder

Sphinx to SATySFi builder.

Note: This is just a trial builder. It will NOT publish to pypi and not implement all of SATySFi features.

Satysfi: https://github.com/gfngfn/SATySFi

Setting
=======

Install
-------

::

   % pip install -e https://github.com/shirou/sphinxcontrib-satysfibuilder


Configure Sphinx
----------------

To enable this extension, add ``sphinxcontrib.satysfibuilder`` module to extensions
option at `conf.py`.

::

   # Enabled extensions
   extensions = ['sphinxcontrib.satysfibuilder']


How to use
=====================

::

  % make satysfi

Repository
==========

https://github.com/shirou/sphinxcontrib-satysfibuilder



License
========

LGPL v3.

Same as SATySFi original. See LICENSE file.
