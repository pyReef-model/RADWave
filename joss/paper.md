---
title: 'RADWave: Python code for ocean surface wave analysis by satellite radar altimeter'
tags:
  - Python
  - satellite radar altimeter
  - waves
  - oceanography
authors:
 - name: Courtney Smith
   orcid: 0000-0002-9556-6626
   affiliation: "1"
 - name: Tristan Salles
   orcid: 0000-0001-6095-7689
   affiliation: "1"
 - name: Ana Vila-Concejo
   orcid: 0000-0003-4069-3094
   affiliation: "1"
affiliations:
 - name: School of Geosciences, The University of Sydney, Australia
   index: 1
date: 20 January 2020
bibliography: paper.bib
---

# Summary

Satellite radar altimeters are an excellent remote sensing technique that can be used to determine significant wave height and wind speed. These measurements can be used in conjunction to calculate wave height, period and power [@Young:2018].

Since the first launch of the *GEOSAT* altimeter in 1985, there has been almost continuous data collection, with only a small gap between 1989-1992 due to no operating satellites. Consequently, analysis of this long-term temporal record can lead to significant insights into inter-annual, seasonal and decadal variations in wave yearly seasonality and decadal trend.

Additionally, the high spatial resolution provided by altimeter data is particularly well-suited for remote regions, or locations where no long-term measurements exist [@Ribal:2019]. An extensive global database of all altimeter missions spanning from 1985-present is available on the Australian Ocean Data Network and has been compiled, calibrated and validated by [@Ribal:2019]. However, for many users, this dataset can be difficult to analyse and only provides significant wave height and wind speed.

# RADWave

![An example of wave analysis perform with RADWave and its plotting capabilities.\label{fig:example}](fig1.jpg)

**RADWave** is Python package that provides a mechanism to access altimeter datasets through web-enabled data services (THREDDS). The package capabilities are illustrated based on the the Australian Ocean Data Network global database [@Ribal:2019]. **RADWave** allows to query over a range of spatial and temporal scales altimeter parameters in specific geographical regions and subsequently calculates significant wave heights, periods, group velocities, average wave energy densities and wave energy fluxes.

**RADWave** can be used to easily calculate past wave conditions and infers long term wave climate variability, providing new insights on wave modal conditions, seasonal changes, long-term trends and associated modulation by climate oscillations. It can also be used to assess locally the impact of wave-generated cyclones in offshore areas.

Along with the documentation a series of Jupyter Notebooks are presented to illustrate the package capability. **RADWave** enhances the ease of access and analysis of altimeter data and is designed for researchers and industry focusing on offshore wave conditions globally. To the authors' knowledge, no open-source code currently exists that provides such capability.


**RADWave** is currently been applied for the characterisation of wave climate and extreme events offshore the Great Barrier Reef and to determine the magnitude and resulting impacts of extreme wave events offshore One Tree Island, Great Barrier Reef.

# Acknowledgements

The authors acknowledge the Integrated Marine Observing System (IMOS) a national collaborative research infrastructure supported by Australian Government and the Australian Ocean Data Network portal (**AODN**) for encouraging and developing the culture of data sharing across the marine science community of Australia.

# References
