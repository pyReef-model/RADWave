Installation
============

**RADWave** is a pure Python package and can be installed via `pip` as well as **Docker**.

Dependencies
------------

You will need a working **Python 3+** (though it will work with Python 2.7) and the following packages are required:
`numpy <http://numpy.org>`_, `scipy <https://scipy.org>`_, `pandas <https://pandas.pydata.org/>`_, `scikit-image <https://scikit-image.org/>`_, `seaborn <https://seaborn.pydata.org>`_, `geopy <https://pypi.org/project/geopy/>`_, `cartopy <https://scitools.org.uk/cartopy/docs/latest/>`_, `netCDF4 <https://pypi.org/project/netCDF4/>`_, `shapely <https://pypi.org/project/Shapely/>`_, `pymannkendall <https://pypi.org/project/pymannkendall/>`_.

The complete list of Dependencies is available in the **src/requirements.txt** file and looks like:

.. code-block:: bash

  numpy>=1.15.0
  pytest
  six>=1.11.0
  setuptools>=38.4.0
  pandas>=0.25
  seaborn>=0.9
  matplotlib>=3.0
  geopy>=1.20
  cartopy>=0.17
  scipy>=1.3
  netCDF4>=1.5.1
  shapely>=1.6.4
  scikit-image>=0.15
  pymannkendall>=0

Installing using pip
--------------------

|PyPI version shields.io|

.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/RADWave
   :target: https://pypi.org/project/RADWave/

You can install **RADWave** package using the latest stable release available via `pip <https://pypi.org/project/RADWave/>`_!

:code:`pip install RADWave`

If you need to install it for different python versions:

.. code-block:: bash

  $ python2 -m pip install radwave
  $ python3 -m pip install radwave

To install the *development version*: **Clone the repository using**

:code:`git clone https://github.com/pyReef-model/RADWave.git`

Navigate into the RADWave directory and run

.. code-block:: bash

  $ cd src/
  $ pip install -r requirements.txt
  $ pip install .


Installing using Docker
-----------------------

Another straightforward installation which does not depend on specific compilers relies on `docker <http://www.docker.com>`_ virtualisation system.

To install the docker image and test it is working:

.. code-block:: bash

  $ docker pull pyreefmodel/radwave:latest
  $ docker run --rm pyreefmodel/radwave:latest help

On Linux, to build the dockerfile locally, we provide a script. First ensure you have checked out the source code from github and then run the script in the Docker directory. If you modify the dockerfile and want to push the image to make it publicly available, it will need to be retagged to upload somewhere other than the pyReef-model repository.

.. code-block:: bash

  $ git checkout https://github.com/pyReef-model/RADWave.git
  $ cd RADWave
  $ source Docker/build-dockerfile.sh

.. note::
  For non-Linux platforms, the use of `Docker Desktop for Mac`_ or `Docker Desktop for Windows`_ is recommended. The docker container to look for is named **pyreefmodel/radwave**!

.. _`Docker Desktop for Mac`: https://docs.docker.com/docker-for-mac/
.. _`Docker Desktop for Windows`: https://docs.docker.com/docker-for-windows/


Testing installation
--------------------

A test is provided to check the correct installation of the **RADWave** package.If you've cloned the source into a directory :code:`RADWave`, you may verify it as follows:

Navigate the directory `src/tests` and run the tests.

.. code-block:: bash

  $ python2 testInstall.py
  $ python3 testInstall.py

You will need to have all dependencies installed.

The following result indicates success.

.. code-block:: bash

  $ Test RADWave installation:: [####################] 100.0% DONE
  $ All tests passed - RADWave installation is completed !
