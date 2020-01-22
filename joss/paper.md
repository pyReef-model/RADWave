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
date: 10 January 2020
bibliography: paper.bib
---
# Summary 
Satellite radar altimeters are an excellent remote sensing technique that can be used to determine significant wave height and wind speed. These measurements can be used in conjunction to calculate wave height, period and power (Young and Donelan 2018). Since the first launch of the *GEOSAT* altimeter in 1985, there has been almost continuous data collection, with only a small gap between 1989-1992 due to no operating satellites. Consequently, analysis of this long-term temporal record can lead to significant insights into inter-annual, seasonal and decadal variations. Additionally, the high spatial resolution provided by altimeter data is particularly well-suited for remote regions, or locations where no long-term measurements exist (Ribal and Young 2019). An extensive database of all altimeter missions spanning from 1985-present is available on the Australian Ocean Data Network (AODN), compiled, calibrated and validated by Ribal and Young (2019). However, for many users, this dataset can be difficult to analyse as it requires high-level coding experience, and only provides significant wave height and wind speed.

# RADWave
**RADWave** is Python code that provides a mechanism to access the AODN calibrated altimeter dataset and to subsequently calculate significant wave height, period and power. The resulting outputs can be assessed over a range of spatial and temporal scales. Application of this code will enable the fast and accurate calculation, and therefore understanding, of past wave conditions and wave climate. Designed for researchers and industry partners focusing on offshore wave conditions globally, RADWave significantly enhances the ease of access and analysis of altimeter data. To the authors' knowledge, no open-source code currently exists that analyses altimeter data and provides an in-depth understanding of modal conditions, seasonal changes, long-term trends and modulation by climate oscillations. 

**RADWave** has already been applied for the characterisation of wave climate and extreme events offshore the Great Barrier Reef (Smith et al., *unpublished*) and in determining the magnitude and resulting impacts of extreme wave events offshore One Tree Island, Great Barrier Reef. An example of a thirty-three year analysis of wave climate is available, focusing offshore Sydney, Australia. 

For collaboration and any questions relating to **RADWave**, please contact Dr Tristan Salles, tristan.salles@sydney.edu.au
