Quick start guide
=================

I/O Options
-----------

The most simple code lines to use **RADWave** functions is summarised below

.. code-block:: python
  :emphasize-lines: 3,4,5,9,11

  import RADWave as rwave

  wa = rwave.waveAnalysis(altimeterURL='../dataset/IMOSURLs.txt', bbox=[152.0,155.0,-36.0,-34.0],
                  stime=[1985,1,1], etime=[2018,12,31])
  wa.processingAltimeterData(altimeter_pick='all', saveCSV = 'altimeterData.csv')
  wa.visualiseData(title="Altimeter data tracks", extent=[149.,158.,-38.,-32.],
                 addcity=['Sydney', 151.2093, -33.8688], markersize=40, zoom=8,
                 fsize=(8, 7), fsave='altimeterdata')
  wa.timeSeries()
  wa.plotTimeSeries(time=[1995,2016], series='H', fsize=(12, 5), fsave='seriesH')
  wh_all = wa.seriesSeasonMonth(series='wh', time=[1998,2018], lonlat=None, fsave='whall', plot=True)


Getting altimeter values from data providers
*****

As previously mentioned, **RADWave** capabilities are illustrated using the Australian Ocean Data Network portal [`AODN <https://portal.aodn.org.au/>`_].
The altimeter dataset are available from the portal by searching for the following data collection:

* :code:`IMOS-SRS Surface Waves Sub-Facility - altimeter wave/wind data`

This global dataset has been compiled and extensively calibrated by [Ribal2019]_ and was regularly updated using altimeter data from 1985 to present. It can be downloaded in 1° x 1° URL files.

.. note::
  The video below illustrates how to select both a spatial bounding box and a temporal extent from the portal and how to export the file containing the :code:`List of URLs` used for wave analysis. This :code:`TXT` file contains a list of :code:`NETCDF` files for each available satellites.

.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="550" src="https://www.youtube.com/embed/MpwkkWzqUHQ?rel=0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </div>

.. important::
    **RADWave** uses the file containing the *list of URLs* to query via THREDDS the remote data. This operation can take several minutes and when looking at a large region it is recommended to divide the analyse in smaller regions and download a series of URLs text file instead of the entire domain directly.

A series of URLs text files is provided with the notebook `examples <https://github.com/pyReef-model/RADWave/tree/master/Notebooks/dataset>`_.

Computing wave parameters
*****

Once the list of :code:`NETCDF` data file has been saved on disk, you will be able to load it by initialising **RADWave** main Python class called :code:`waveAnalysis`.
For a detail overview of the options available in this class, the user is invited to look at the `waveAnalysis API`_.

.. code-block:: python
    import RADWave as rwave

    wa = rwave.waveAnalysis(altimeterURL='../dataset/IMOSURLs.txt', bbox=[152.0,155.0,-36.0,-34.0],
                    stime=[1985,1,1], etime=[2018,12,31])



.. note::
  In cases where one want to query altimeter data along a specific path such as a cyclone track, it will be necessary to provide a second file with the recorded track geographical coordinates and associated time. The file will be a :code:`CSV` file with in the header the following keyword names :code:`lon`, :code:`lat` & :code:`datetime`. An example of such a file is provided with the notebooks based on dataset exported from the Bureau of Meteorology (`BOM <http://www.bom.gov.au/cyclone/history/tracks/>`). In such cases, the call to :code:`waveAnalysis` will take the form:

.. code-block:: python
    import RADWave as rwave

    wa = rwave.waveAnalysis(altimeterURL='../dataset/IMOSURLs.txt', bbox=[152.0,155.0,-36.0,-34.0],
                    stime=[1985,1,1], etime=[2018,12,31])

After class initialisation querying the actual dataset is realised by calling the :code:`processingAltimeterData` function (option available in the `processingAltimeterData API`_)

.. code-block:: python
    wa.processingAltimeterData(altimeter_pick='all', saveCSV = 'altimeterData.csv')

The function can take some times to execute depending on the number of :code:`NETCDF` files to load and the size of the dataset to query.

.. note::
    This function relies mostly on Pandas (library) and writes the processed dataset to file that can be later used to access more efficiently altimeter information.

In case where the *processingAltimeterData* function has already been executed, one can load directly the processed data from the created CSV file in a more efficient way by running the :code:`readingAltimeterData` function as follow:


.. code-block:: python
    wa.readingAltimeterData(saveCSV = 'altimeterData.csv')




Outputs
*******

.. code-block:: python
  :emphasize-lines: 6,7

  import bioLEC as bLEC

  biodiv = bLEC.landscapeConnectivity(filename='pathtofile.csv')
  biodiv.computeLEC()

  biodiv.writeLEC('result')
  biodiv.viewResult(imName='plot.png')

Once the :code:`computeLEC()` function (see `API compute LEC`_) has been ran, the result are then available in different forms.

From the :code:`writeLEC` function (see `API write LEC`_), the user can first save the dataset in :code:`CSV` and :code:`VTK` formats containing the X,Y,Z coordinates as well as the computed LEC and normalised LEC (_nLEC_).

Then several figures can be created showing **maps of elevation and LEC values** as well as graphs of LEC and elevation frequency as a function of site elevation (such as the figure presented below). In some functions, one can plot the average and error bars of LEC within elevational bands.


Available plotting functions are provided below:

* :code:`viewResult`
* :code:`viewElevFrequency`
* :code:`viewLECFrequency`
* :code:`viewLECZbar`
* :code:`viewLECZFrequency`

For a complete list of available options, users need to go to the `API documentation <https://biolec.readthedocs.io/en/latest/bioLEC.html#bioLEC.LEC.landscapeConnectivity.viewLECFrequency>`_.

Running examples
----------------

There are different ways of using the **RADWave** package. If you used a local install with :code:`pip`, you can download the *Jupyter Notebooks* provided in the Github repository...

.. code-block:: bash

  $ git clone https://github.com/pyReef-model/RADWave.git


Binder
***************

The series of *Jupyter Notebooks* can also be ran with **Binder** that opens those notebooks in an executable environment, making the package immediately reproducible without having to perform any installation.

.. image:: https://mybinder.org/badge_logo.svg
  :target: https://mybinder.org/v2/gh/pyReef-model/RADWave/binder?filepath=Notebooks%2F0-StartHere.ipynb

This is by far the most simple method to test and try this package, just
launch the demonstration at `RADWave-live (mybinder.org) <https://mybinder.org/v2/gh/pyReef-model/RADWave/binder?filepath=Notebooks%2F0-StartHere.ipynb>`_!

.. image:: ../RADWave/Notebooks/images/binder.jpg
   :scale: 30 %
   :alt: boundary conditions
   :align: center

Docker
***************

Another straightforward installation that again does not depend on specific compilers relies on the **docker virtualisation system**. Simply look for the following Docker container **pyreefmodel/radwave**.

.. note::
  For non-Linux platforms, the use of `Docker Desktop for Mac`_ or `Docker Desktop for Windows`_ is recommended.

.. _`Docker Desktop for Mac`: https://docs.docker.com/docker-for-mac/
.. _`Docker Desktop for Windows`: https://docs.docker.com/docker-for-windows/


.. _`waveAnalysis API`: https://radwave.readthedocs.io/en/latest/RADWave.html#RADWave.altiwave.waveAnalysis
.. _`processingAltimeterData API`: https://radwave.readthedocs.io/en/latest/RADWave.html#RADWave.altiwave.waveAnalysis.processingAltimeterData


.. _`API compute LEC`: https://biolec.readthedocs.io/en/latest/bioLEC.html#bioLEC.LEC.landscapeConnectivity.computeLEC
.. _`API write LEC`: https://biolec.readthedocs.io/en/latest/_modules/bioLEC/LEC.html#landscapeConnectivity.writeLEC


.. [Ribal2019] Ribal, A. & Young, I. R. -
    33 years of globally calibrated wave height and wind speed data based on altimeter observations. **Scientific Data** 6(77), p.100, 2019.
