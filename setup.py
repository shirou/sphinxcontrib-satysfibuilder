# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
Sphinx SATySFi builder.

SATySFi: https://github.com/gfngfn/SATySFi
'''

requires = ['Sphinx>=1.6', 'setuptools']

setup(
    name='sphinxcontrib-satysfibuilder',
    version='0.0.1',
    url='http://github.com/shirou/sphinxcontrib-satysfibuilder',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-satysfibuilder',
    license='LGPL',
    author='WAKAYAMA Shirou',
    author_email='shirou.faw@gmail.com',
    description='Sphinx satysfibuilder extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
