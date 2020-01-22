# RADWave - _Wave analysis from Altimer data_


[![Docker Cloud Automated build](https://img.shields.io/docker/automated/pyreefmodel/radwave)](https://hub.docker.com/r/pyreefmodel/radwave)
[![PyPI](https://img.shields.io/pypi/v/RADWave)](https://pypi.org/project/RADWave/) [![Documentation Status](https://readthedocs.org/projects/radwave/badge/?version=latest)](https://radwave.readthedocs.io/en/latest/?badge=latest)

**RADWave** documentation is found at [**radwave.readthedocs.io**](https://biolec.readthedocs.io/)

**RADWave** is a python package built to characterise *wave conditions* based on altimeter data.

![altimeter](https://github.com/pyReef-model/RADWave/blob/master/src/RADWave/Notebooks/images/img2.jpg?raw=true)

> **LEC** quantifies the closeness of a site to all others with **similar elevation**. It measures how easily a **species living in a given patch can spread and colonise other patches**. It is assumed to be **elevation-dependent** and the metric depends on how often a species adapted to a given elevation *needs to travel outside its optimal elevation range* when moving from its patch to any other in the landscape [Bertuzzo et al., 2016].


## Installation

### Dependencies

You will need **Python 3.5+**.
Also, the following packages are required:

 - [`numpy`](http://numpy.org)
 - [`scipy`](https://scipy.org)
 - [`pandas`](https://pandas.pydata.org/)
 - [`scikit-image`](https://scikit-image.org/)
 - [`seaborn`](https://seaborn.pydata.org)
 - [`geopy`](https://pypi.org/project/geopy/)
 - [`cartopy`](https://scitools.org.uk/cartopy/docs/latest/)
 - [`netCDF4`](https://pypi.org/project/netCDF4/)
 - [`shapely`](https://pypi.org/project/Shapely/)
 - [`pymannkendall`](https://pypi.org/project/pymannkendall/)

### Installing using pip

You can install `RADWave` using the
[`pip package manager`](https://pypi.org/project/pip/) with your version of Python:

```bash
python3 -m pip install RADWave
```

### Installing using Docker

A more straightforward installation which does not depend on specific compilers relies on the [docker](http://www.docker.com) virtualisation system.

To install the docker image and test it is working:

```bash
   docker pull pyreefmodel/radwave:latest
   docker run --rm pyreefmodel/radwave:latest help
```

To build the dockerfile locally, we provide a script. First ensure you have checked out the source code from github and then run the script in the Docker directory. If you modify the dockerfile and want to push the image to make it publicly available, it will need to be retagged to upload somewhere other than the GEodels repository.

```bash
git checkout https://github.com/pyReef-model/RADWave.git
cd RADWave
source Docker/build-dockerfile.sh
```

## Usage

### Binder & docker container

Launch the demonstration at [mybinder.org](https://mybinder.org/v2/gh/pyReef-model/RADWave/binder?filepath=Notebooks%2F0-StartHere.ipynb)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pyReef-model/RADWave/binder?filepath=Notebooks%2F0-StartHere.ipynb)


![cyclone](https://github.com/pyReef-model/RADWave/blob/master/src/RADWave/Notebooks/images/img1.jpg?raw=true)


Another option will be to use the Docker container available through Kitematic **pyreefmodel/radwave**.

[![Docker Cloud Automated build](https://img.shields.io/docker/automated/pyreefmodel/radwave)](https://hub.docker.com/r/pyreefmodel/radwave)

## Collaborations

### How to contribute?

**We welcome all kinds of contributions!** Please get in touch if you would like to help out.

 > Everything from **code** to **notebooks** to **examples** and **documentation** are all equally valuable so please don't feel you can't contribute.

To contribute please **fork the project make your changes and submit a pull request**. We will do our best to work through any issues with you and get your code merged into the main branch.

If you found a bug, have questions, or are just having trouble with **bioLEC**, you can:

+ join the **RADWave User Group on Slack** by sending an email request to: tristan.salles@sydney.edu.au
+ open an issue in our [issue-tracker](https://github.com/pyReef-model/RADWave/issues/new) and we'll try to help resolve the concern.

### Where to find support?

Please feel free to submit new issues to the [issue-log](https://github.com/pyReef-model/RADWave/issues/new) to request new features, document new bugs, or ask questions.


### License

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU Lesser General Public License** as published by the **Free Software Foundation**, either version 3 of the License, or (at your option) any later version.

  > This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
  You should have received a copy of the GNU Lesser General Public License along with this program.  If not, see http://www.gnu.org/licenses/lgpl-3.0.en.html.
  
  
# Altimeter waves
This repository shows how to calculate short term wave conditions and long term wave climate statistics from satellite radar altimeters. It can also be used to determine wind conditions, however wind is not explicitly discussed in this project. Altimeters are widely established as an accurate remote sensing technique, and are particularly advantageous for remote areas, and locations with no long term monitoring of waves (Young et al. 2011). 

# References

  1. Ribal, A. and Young, I.R., 2019. 33 years of globally calibrated wave height and wind speed data based on altimeter observations. **Scientific Data** 6(77), p.100.

  1. Young, I. R., Zieger, S. and Babanin, A. V., 2011. Global trends in wind speed and wave height. **Science** 332(6028), p451–455.
