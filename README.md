# RADWave - _Wave analysis from Altimer data_


[![Docker Cloud Automated build](https://img.shields.io/docker/automated/pyreefmodel/radwave)](https://hub.docker.com/r/pyreefmodel/radwave)
[![PyPI](https://img.shields.io/pypi/v/RADWave)](https://pypi.org/project/RADWave/) [![Documentation Status](https://readthedocs.org/projects/radwave/badge/?version=latest)](https://radwave.readthedocs.io/en/latest/?badge=latest)

**RADWave** documentation is found at [**radwave.readthedocs.io**](https://biolec.readthedocs.io/)

**RADWave** is a python package built to characterise *wave conditions* based on altimeter data.

![bioLEC](https://github.com/Geodels/bioLEC/blob/master/Notebooks/images/intro.jpg?raw=true)


**LEC** quantifies the closeness of a site to all others with **similar elevation**. It measures how easily a **species living in a given patch can spread and colonise other patches**. It is assumed to be **elevation-dependent** and the metric depends on how often a species adapted to a given elevation *needs to travel outside its optimal elevation range* when moving from its patch to any other in the landscape [Bertuzzo et al., 2016].


# Altimeter waves
This repository shows how to calculate short term wave conditions and long term wave climate statistics from satellite radar altimeters. It can also be used to determine wind conditions, however wind is not explicitly discussed in this project. Altimeters are widely established as an accurate remote sensing technique, and are particularly advantageous for remote areas, and locations with no long term monitoring of waves (Young et al. 2011). 

# Installation

RADWave accesses altimeter data through the Australian Ocean Data Network ([AODN]) (https://portal.aodn.org.au/search). This dataset was compiled and extensively calibrated by Ribal and Young (2019). It is regularly updated using altimeter data from 1985-present, and can be downloaded in 1° x 1° URL files. Notebook1 uses a txt file (named IMOSURLs.txt) that directly extracts data from this portal. To access altimeter data for the area of interest, navigate to the AODN data portal and select IMOS-SRS Surface Waves Sub-Facility - altimeter wave/wind data. Determine the spatial and temporal bounding boxes for area of interest. Press next, and select "Download as...", selecting "List of URLs". Save and rename this file as "IMOSURLs.txt", which will be used in Notebook1-Define Area.

# Dependencies
Python3 or later is required, in addition to the following packages:

* numpy
* pandas
* netCDF4
* datetime
* re
* seaborn
* pymannkendall
* matplotlib
* math


# Collaborations and issues
Please let us know if you would like to contribute - can be anything from code, notebooks or examples, they all further understanding and development of RADWave. 

To contribute please fork the project make your changes and submit a pull request. We will do our best to work through any issues with you and get your code merged into the main branch.


If you found a bug or have any questions please email Tristan Salles at tristan.salles@sydney.edu.au


# License





# References
Ribal, A. and Young, I.R., 2019. 33 years of globally calibrated wave height and wind speed data based on altimeter observations. *Scientific Data* 6(77), p.100.

Young, I. R., Zieger, S. and Babanin, A. V., 2011. Global trends in wind speed and wave height. *Science 332*(6028), p451–455.
