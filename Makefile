test:
	pip uninstall -y sphinxcontrib-satysfibuilder && pip install .
	py.test
