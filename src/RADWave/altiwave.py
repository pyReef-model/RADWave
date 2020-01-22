#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*
# Copyright (c) 2020 Tristan Salles
# Licensed under the GNU LGPL Version 3

import io
import gc
import re
import sys
import math
import time
import errno
import requests
import numpy as np
import pandas as pd

import scipy
from functools import reduce
from scipy.spatial import cKDTree as _cKDTree

# For readthedoc...
try:
    import netCDF4
    from netCDF4 import Dataset as NetCDFFile
    from netCDF4 import num2date, date2num, date2index
    import datetime as dt
except ImportError:
    print('netCDF4 is required and needs to be installed via pip')
    pass

# For readthedoc...
try:
    import cartopy
    import cartopy.geodesic
    import cartopy.crs as ccrs
    import cartopy.io.img_tiles as cimgt
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
except ImportError:
    print('cartopy is required and needs to be installed via pip')
    pass

# For readthedoc...
try:
    import pymannkendall as mk
except ImportError:
    print('pymannkendall is required and needs to be installed via pip')
    pass

# For readthedoc...
try:
    import seaborn as sns
except ImportError:
    print('seaborn is required and needs to be installed via pip')
    pass

# For readthedoc...
try:
    import shapely
    from shapely.geometry.polygon import LinearRing
except ImportError:
    print('shapely is required and needs to be installed via pip')
    pass

# For readthedoc...
try:
     import geopy.distance
except ImportError:
    print('geopy is required and needs to be installed via pip')
    pass

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.transforms import offset_copy
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

plt.rcParams['mathtext.fontset'] = 'cm'

class waveAnalysis(object):
    """
    **RadWave** is a package to perform wave analysis using *Radar Altimeter Data*. Radar altimeters are mounted on satellites
    and measure a footprint of the ocean directly under the satellite (approx. 5-7 km wide). When the water surface is calm and flat,
    the reflection of the radar pulse back to the altimeter is almost instantaneous. In contrast, when waves are present the pulse
    is first reflected at the crest of the wave, then progressively reflected as the pulse reaches the wave trough.

    Method:
        Calibrated altimeter dataset provide **wave height** and **wind speed** through a series of equations described in
        [RibalYoung2019]

    .. [RibalYoung2019]   Ribal, A. & Young, I. R. -
	   33 Years of Globally Calibrated Wave Height and Wind Speed Data Based on Altimeter Observations. Sci Data 6, 77, `DOI: 10.1038/s41597-019-0083-9`_, 2019.

    .. _`DOI: 10.1038/s41597-019-0083-9`: https://www.nature.com/articles/s41597-019-0083-9

    Data:
        Altimeter data are read from netcdf files that are provided via a list of URLs. Here we propose a series of examples using the Australian Ocean Data
        Network (AODN) (`https://portal.aodn.org.auIMOS`_) but other web portals could be easely added.

    .. _`https://portal.aodn.org.auIMOS`: https://portal.aodn.org.auIMOS

    Args:
        cycloneCSV (str): path as a csv file containing cyclone tracks with in the header the following names *lon*, *lat* & *datetime* [default: None]
        altimeterURL (str): list of NetCDF URLs downloaded from the wave data portal containing the radar altimeter data [default: None]
        bbox (list): bounding box specifying the geographical extent of the uploaded dataset following the convention [lon min,lon max,lat min,lat max]  [default: None]
        stime (list):  starting time of wave climate analysis following the convention [year, month, day] [default: None]
        etime (list): ending time of wave climate analysis following the convention [year, month, day] [default: None]
        satNames (list): list of satellites to use for the analysis - AODN portal provide the record from 10 satellites for altimeter data [default: None]

    Note:
        This remote sensing technique does not provide individual wave statistics, but rather returns the **average value over satellite
        footprint**, up to 7 km wide.
    """

    def __init__(self, cycloneCSV=None, altimeterURL=None, bbox=None, stime=None, etime=None, satNames=None, test=False):

        self.test = test
        if cycloneCSV is not None:
            try:
                with open(str(cycloneCSV)) as file:
                    pass
            except IOError as e:
                print("Unable to open file ",str(cycloneCSV))

            self.cyclone = pd.read_csv(str(cycloneCSV), sep=r',', engine='c', header=0, \
                                na_filter=False, low_memory=False)
            column_list = ('lat', 'lon', 'datetime')
            for col in column_list:
                if col not in self.cyclone.columns:
                    raise ValueError('Both columns lat, lon and datetime are required in the cyclone track file')

            self.cyclone['datetime']= pd.to_datetime(self.cyclone['datetime'])
        else:
            self.cyclone = None
        self.cyclone_data = None
        self.timeseries = None

        if altimeterURL is not None:

            try:
                with open(str(altimeterURL)) as file:
                    pass
            except IOError as e:
                print("Unable to open file ",str(altimeterURL))

            if satNames is None:
                satNames = ['JASON-2','JASON-3','SARAL','SENTINEL-3A','CRYOSAT-2','ENVISAT','GEOSAT','ERS-2','GFO','TOPEX']

            self.satNb = len(satNames)
            self.allURL = []
            self.nameSat = []
            for k in range(self.satNb):
                satFile = self._extractURLsatellite( fileURL = altimeterURL, satName = satNames[k])
                if len(satFile)>0:
                    self.allURL.append(satFile)
                    ncs = NetCDFFile(satFile[0])
                    self.nameSat.append(ncs.title.split(' ', 1)[0])

            # latitude and longitude
            if bbox[0]>=bbox[1]:
                raise ValueError('Error wrong definition of min and max lon')
            if bbox[2]>=bbox[3]:
                raise ValueError('Error wrong definition of min and max lat')
            self.lonmin = bbox[0]
            self.lonmax = bbox[1]
            self.latmin = bbox[2]
            self.latmax = bbox[3]

            # Date
            self.start_date = dt.datetime(stime[0],stime[1],stime[2])
            self.end_date = dt.datetime(etime[0],etime[1],etime[2])
            delta_time = self.end_date - self.start_date
            dhours = delta_time.total_seconds()/3600.
            if dhours<=0.:
                raise ValueError("Error the defined start time 'stime' is set after the end time 'etime'.")

        return

    def _test_progress(self, job_title, progress):
        length = 20
        block = int(round(length*progress))
        msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
        if progress >= 1: msg += " DONE\r\n"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def _extractURLsatellite(self, fileURL, satName):
        """
        Function to convert the list of URL’s generated by the IMOS portal to a list of OPeNDAP data URL’s for specific satellites.
        From downloaded dataset from the AODN portal user choose the options *List of URLs* to obtain NetCDF files.
        IMOS NetCDF files are accessible via an OPeNDAP catalog at : `IMOScatalog`_

        .. _`IMOScatalog`: http://thredds.aodn.org.au/thredds/catalog/IMOS/catalog.html

        The advantage of the THREDDS catalog is that the data files do not have to be downloaded to your local machine first – the OPeNDAP data URL can be parsed into Python.

        Note:
            The list of URL’s generated by the IMOS portal can be converted to a list of OPeNDAP data URL’s by replacing string *http://data.aodn.org.au/IMOS/opendap* with
            *http://thredds.aodn.org.au/thredds/dodsC/IMOS*.

        Args:
            fileURL (str): list of NetCDF URLs downloaded from the wave data portal containing the radar altimeter data
            satNames (list): list of satellites to use for the analysis - AODN portal provide the record from 10 satellites for altimeter data

        Returns:
            getFiles : list of OPeNDAP data URL’s for given satellites
        """

        getFiles = []

        with open(fileURL) as f:
            for line in f:
                if re.search(r"%s"%satName, line):
                    changeURL = re.sub('http://data.aodn.org.au', 'http://thredds.aodn.org.au/thredds/dodsC', line)
                    getFiles.append(changeURL)

        return getFiles

    def processingAltimeterData(self, altimeter_pick='all', saveCSV = 'altimeterData.csv'):
        """
        From the list of OPeNDAP data URL’s this function extracts the altimeter data information.

        The function can take some times to execute depending on the number of files to load and the size of the dataset to interogate.

        Todo:
            Here we use default NetCDF variables keys based on the IMOS AODN dataset: 'LATITUDE'/'LONGITUDE'/'WSPD_CAL'...
            In the future, we could provide additional capabilities to extract additional keys by reading each file variables [vars = data_nc.variables.keys()]

        Note:
            This function relies mostly on Pandas (library) and writes the processed dataset to file that can be later used to access more efficiently
            altimeter information.

        Warning:
            Because the data is accessed via the THREDDS catalog, there can be a latency when querying the NetCDF files.

        Args:
            altimeter_pick (list): list of satellites to use for the analysis as an example AODN portal provide the record from 10 satellites for altimeter data [default: 'all']
            saveCSV (str): filename used to save processed altimeter data obtained from the OPeNDAP web service [default: 'altimeterData.csv']
        """

        if not self.test:
            print('Processing Altimeter Dataset \n')

        t0 = time.clock()
        p = 0
        step = 0
        steps = 58
        for u in range(len(self.allURL)):
            picked_url = self.allURL[u]

            if altimeter_pick == self.nameSat[u] or altimeter_pick == 'all':
                for k in range(len(picked_url)):

                    if self.test:
                        step += 1
                        self._test_progress("Test RADWave installation:", step/steps)

                    ncs = NetCDFFile(picked_url[k])
                    if k == 0 and not self.test:
                        print('   +  name {:<11s} / number of tracks {:<4d}'.format(self.nameSat[u],len(picked_url)))

                    # Get desired bounding box
                    lats = ncs.variables['LATITUDE'][:]
                    lons = ncs.variables['LONGITUDE'][:]
                    latbound = np.where(np.logical_and(lats>=self.latmin,lats<=self.latmax))[0]
                    lonbound = np.where(np.logical_and(lons>=self.lonmin,lons<=self.lonmax))[0]

                    # Get desired time interval
                    time_var = ncs.variables['TIME']
                    tt = ncs.variables['TIME'][:]
                    timing = netCDF4.num2date(tt,time_var.units)
                    self.time_units = time_var.units
                    timebound = np.where(np.logical_and(timing>=self.start_date,timing<=self.end_date))[0]

                    reduceID = reduce(np.intersect1d, (latbound,lonbound,timebound))

                    if len(reduceID)>0:
                        ws = ncs.variables['WSPD_CAL'][:]
                        if self.nameSat[u] == 'SARAL':
                            wh = ncs.variables['SWH_KA_CAL'][:]
                            qc = ncs.variables['SWH_KA_quality_control'][:]
                            back = ncs.variables['SIG0_KA'][:]
                        else:
                            wh = ncs.variables['SWH_KU_CAL'][:]
                            qc = ncs.variables['SWH_KU_quality_control'][:]
                            back = ncs.variables['SIG0_KU'][:]

                        hqlimit = np.where(np.logical_and(wh>0,qc==1))[0]
                        ids = np.intersect1d(hqlimit,reduceID)

                        data = {'ws': ws[ids],
                                'wh': wh[ids],
                                'qc': qc[ids],
                                'back': back[ids],
                                'lats': lats[ids],
                                'lons': lons[ids],
                                'time': tt[ids]}
                        df = pd.DataFrame(data)

                        df2 = pd.DataFrame(timing[ids],columns=['date'])
                        df2['year'] = pd.DatetimeIndex(df2['date']).year
                        df2['month'] = pd.DatetimeIndex(df2['date']).month
                        df2['day'] = pd.DatetimeIndex(df2['date']).day

                        dataframe = pd.concat([df,df2], axis=1, sort=False)
                        dataframe = dataframe.drop(['date'], axis=1)

                        time_m = dataframe.groupby(['year', 'month', 'day'])[['time']].apply(np.median)
                        time_m.name = 'time'
                        qc_m = dataframe.groupby(['year', 'month', 'day'])[['qc']].apply(np.median)
                        qc_m.name = 'qc'
                        back_m = dataframe.groupby(['year', 'month', 'day'])[['back']].apply(np.median)
                        back_m.name = 'back'
                        wh_m = dataframe.groupby(['year', 'month', 'day'])[['wh']].apply(np.median)
                        wh_m.name = 'wh'
                        ws_m = dataframe.groupby(['year', 'month', 'day'])[['ws']].apply(np.median)
                        ws_m.name = 'ws'
                        lats_m = dataframe.groupby(['year', 'month', 'day'])[['lats']].apply(np.median)
                        lats_m.name = 'lat'
                        lons_m = dataframe.groupby(['year', 'month', 'day'])[['lons']].apply(np.median)
                        lons_m.name = 'lon'
                        frame = pd.concat([qc_m,wh_m,ws_m,back_m,lats_m,lons_m,time_m], axis=1, sort=False)
                        frame['altimeter'] = self.nameSat[u]
                        if p>0:
                            combineframe = pd.concat([combineframe,frame],sort=True)
                        else:
                            combineframe = frame
                            p = p+1

        if p>0:
            if not self.test:
                self.saveCSV = saveCSV
                combineframe.to_csv(str(self.saveCSV),columns=['lat', 'lon', 'wh', 'time', 'ws'], sep=' ', index=False ,header=1)
                altiData = pd.read_csv(str(self.saveCSV), sep=r'\s+', engine='c', header=0, na_filter=False, low_memory=False)
                data = altiData.sort_values(by=['time'])
                data = data.replace(r'^\s*$', np.nan, regex=True)
                data = data.dropna()
                self.lat = np.asarray(data.values[:,0], dtype=np.float64)
                self.lon = np.asarray(data.values[:,1], dtype=np.float64)
                self.wh = np.asarray(data.values[:,2], dtype=np.float64)
                self.times = data.values[:,3]
                self.ws = np.asarray(data.values[:,4], dtype=np.float64)
                print(' \nProcessing altimeter dataset took: ',int(time.clock()-t0),'s')
            else:
                print('\nAll tests passed - RADWave installation is completed !\n')
        else:
            print('No altimeter data found...')

        return

    def readingAltimeterData(self, saveCSV=None):
        """
        In case where the *processingAltimeterData* function has already been executed, one can load directly the processed data from the created CSV file.

        Args:
            saveCSV (str): filename used to save processed altimeter data obtained from the OPeNDAP web service [default: None]
        """

        if saveCSV is not None:
            self.saveCSV = saveCSV

        try:
            with open(str(self.saveCSV)) as file:
                pass
        except IOError as e:
            print("Unable to open altimeter data file ",str(self.saveCSV))

        print('Reading Processed Altimeter Dataset \n')

        picked_url = self.allURL[0]
        ncs = NetCDFFile(picked_url[0])
        time_var = ncs.variables['TIME']
        self.time_units = time_var.units

        altiData = pd.read_csv(str(self.saveCSV), sep=r'\s+', engine='c', header=0, na_filter=False, low_memory=False)
        data = altiData.sort_values(by=['time'])
        data = data.replace(r'^\s*$', np.nan, regex=True)
        data = data.dropna()

        self.lat = np.asarray(data.values[:,0], dtype=np.float64)
        self.lon = np.asarray(data.values[:,1], dtype=np.float64)
        self.wh = np.asarray(data.values[:,2], dtype=np.float64)
        self.times = data.values[:,3]
        self.ws = np.asarray(data.values[:,4], dtype=np.float64)

        return

    def plotCycloneTracks(self, title="Cyclone data tracks", markersize=100, zoom=4, extent=None, fsize=(12, 10), fsave=None):
        """
        This function **plots** and **saves** in a figure a specific cyclone track loaded during the initialisation phase of the waveAnalysis class.

        Example of cyclone track for Australia can be found on the Australian Bureau of Meteorology (BOM_).

        .. _BOM: http://www.bom.gov.au/cyclone/history/tracks/

        Args:
            title (str): title for the figure [default: "Cyclone data tracks"]
            markersize (int): size of the markers used to specify cyclone tracks [default: 100]
            zoom (int): given target zoom for the target domain background (must be a value >= 1) [default: 4]
            extent (int): geographical extent of the figure following the convention [lon min,lon max,lat min,lat max]  [default: None]
            fsize : size of the image [default: (12,10)]
            fsave (str): saved image name without extension that will be written as a PNG file [default: None]

        Note:
            This function relies on **cartopy** and **matplotlib** libraries. We use cartopy’s ability to draw map tiles which are downloaded on demand
            from the **Stamen tile server**.

        Todo:
            There are some plotting problems for dataset spanning beyond the 180 degree meridian that will need to be fixed.

        Warning:
            The cyclone tracks contains the following variables *lon*, *lat* & *datetime*.
        """

        # Create a Stamen terrain background instance.
        stamen_terrain = cimgt.Stamen('terrain-background')

        fig = plt.figure(figsize=fsize)

        # Create a GeoAxes in the tile's projection
        ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs) #ccrs.PlateCarree(180))

        # Limit the extent of the map to a small longitude/latitude range
        if extent is None:
            ax.set_extent([self.lonmin, self.lonmax, self.latmin, self.latmax], crs=ccrs.PlateCarree())
        else:
            ax.set_extent([extent[0], extent[1], extent[2], extent[3]], crs=ccrs.PlateCarree())

        # Add the Stamen data
        ax.add_image(stamen_terrain, zoom)

        ax.coastlines(resolution='10m')

        # Cyclone track
        clon = self.cyclone['lon'].to_numpy()
        clat = self.cyclone['lat'].to_numpy()
        for k in range(len(clon)-1):
            plt.plot([clon[k],clon[k+1]], [clat[k],clat[k+1]],
                 color='r', linewidth=3, alpha=0.5,
                 transform=ccrs.PlateCarree(), zorder=1)

        plt.scatter([clon],[clat], marker='o', color='r', s=markersize, edgecolor='black', linewidth='0.5',
                alpha=1, transform=ccrs.PlateCarree(), zorder=5)

        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
        text_transform = offset_copy(geodetic_transform, units='dots', y=-30)

        cycloneyear = self.cyclone['datetime'].dt.year
        cycloneday = self.cyclone['datetime'].dt.day
        cyclonemonth = self.cyclone['datetime'].dt.month
        cyclonehour = self.cyclone['datetime'].dt.hour
        cyclonedate = []
        for k in range(len(clon)):
            cyclonedate.append(str(cycloneday[k])+'/'+str(cyclonemonth[k])+'\n '+str(cyclonehour[k])+'h')
        ax.set_title(title+' records starting on the '+str(cycloneday[0])+'/'+str(cyclonemonth[0])+'/'+str(cycloneyear[0]))

        for k in range(3,len(clon),4):
            ax.text(clon[k], clat[k], cyclonedate[k], color='navy',
                                verticalalignment='center', horizontalalignment='center',
                                transform=text_transform,
                                bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'), zorder=10)

            plt.scatter(clon[k],clat[k], marker='o', color='navy', s=markersize, edgecolor='black', linewidth='0.5',
                    alpha=1, transform=ccrs.PlateCarree(), zorder=10)

        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='k', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        plt.show()

        if fsave is not None:
            fig.savefig(fsave, dpi=100)
            print('Figure saved: ',fsave)

        return

    def visualiseData(self, title="Altimeter data coordinates", extent=None, addcity=None, markersize=100, zoom=4, fsize=(12, 10), fsave=None):
        """
        This function **plots** and **saves** in a figure the geographical coordinates of processed altimeter data.
        In case where a cyclone track has also been loaded during the initialisation phase of the waveAnalysis class, the cyclone path is also
        added to the figure.

        Args:
            title (str): title for the figure [default: "Altimeter data coordinates"]
            extent (int): geographical extent of the figure following the convention [lon min,lon max,lat min,lat max]  [default: None]
            addcity (list): defined a specific location using the following convention ['City Name', longitude, latitude] [default: None]
            markersize (int): size of the markers used to specify cyclone tracks [default: 100]
            zoom (int): given target zoom for the target domain background (must be a value >= 1) [default: 4]
            fsize : size of the image [default: (12,10)]
            fsave (str): saved image name without extension that will be written as a PNG file [default: None]

        Note:
            This function relies on **cartopy** and **matplotlib** libraries. We use cartopy’s ability to draw map tiles which are downloaded on demand
            from the **Stamen tile server**.

        Todo:
            There are some plotting problems for dataset spanning beyond the 180 degree meridian that will need to be fixed.
        """

        # Create a Stamen terrain background instance.
        stamen_terrain = cimgt.Stamen('terrain-background')

        fig = plt.figure(figsize=fsize)

        # Create a GeoAxes in the tile's projection.
        ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
        # Limit the extent of the map to a small longitude/latitude range
        if extent is None:
            ax.set_extent([self.lonmin, self.lonmax, self.latmin, self.latmax], crs=ccrs.Geodetic())
        else:
            ax.set_extent([extent[0], extent[1], extent[2], extent[3]], crs=ccrs.Geodetic())

        # Add the Stamen data
        ax.add_image(stamen_terrain, zoom)

        ax.set_title(title)
        ax.coastlines(resolution='10m')

        ax.scatter([self.lon],[self.lat], marker='o', color='coral', s=markersize, edgecolor='black', linewidth='0.5',
                alpha=0.7, transform=ccrs.Geodetic())

        # Use the cartopy interface to create a matplotlib transform object
        # for the Geodetic coordinate system.
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
        text_transform = offset_copy(geodetic_transform, units='dots', x=-12)

        # Cyclone track
        if self.cyclone is not None:
            clon = self.cyclone['lon'].to_numpy()
            clat = self.cyclone['lat'].to_numpy()
            for k in range(len(clon)-1):
                plt.plot([clon[k],clon[k+1]], [clat[k],clat[k+1]],
                     color='navy', linewidth=3, alpha=1.,
                     transform=ccrs.PlateCarree(), zorder=1)

        # Add a marker for a given city.
        if addcity is not None:
            name_city = addcity[0]
            lon_city = addcity[1]
            lat_city = addcity[2]
            ax.scatter(lon_city, lat_city, marker='o', color='navy', s=100, edgecolor='black', linewidth='0.5',
                    alpha=0.7, transform=ccrs.Geodetic())
            ax.text(lon_city, lat_city, name_city,
                        verticalalignment='center', horizontalalignment='right',
                        transform=text_transform,
                        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'))

        # Add bounding box of interest
        rlons = [self.lonmin, self.lonmin, self.lonmax, self.lonmax]
        rlats = [self.latmin, self.latmax, self.latmax, self.latmin]
        ring = LinearRing(list(zip(rlons, rlats)))
        if self.cyclone is None:
            ax.add_geometries([ring], ccrs.PlateCarree(), facecolor='none', edgecolor='k', linewidth=2)
        else:
            ax.add_geometries([ring], ccrs.PlateCarree(), facecolor='none', edgecolor='k', alpha=0.8, linewidth=2)

        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='k', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        plt.show()

        if fsave is not None:
            fig.savefig(fsave, dpi=100)
            print('Figure saved: ',fsave)

        return

    def _waveAge(self, H, U, grav=9.80665):
        """
        This function computes the wave age from the following altimeter data: *wave height* and *surface wind speed*.

        Args:
            H (numpy array): significant wave height in metres
            U (numpy array): surface wind speed in metres per second
            grav (float): acceleration of gravity (m/s2) [default: 9.80665]

        Returns:
            eps (numpy array): wave age following Remya et al. (2010) algorithm
        """

        grav2 = grav**2
        wh2 = np.square(H)
        u4 = np.power(U,4)
        tmp = np.divide(wh2*grav2,u4)
        eps = 3.25*np.power(tmp,0.31)

        return eps

    def wavePeriod(self, H, U, grav=9.80665):
        """
        This function computes the wave period from the following altimeter data: *wave height* and *surface wind speed*.

        Method:
            Altimeters do not directly measure wave period, an essential component to adequately characterise wave climate.
            To calculate wave period from altimeter backscatter we use the algorithm proposed by Remya et al. (2010) based on
            wind speed (U) and significant wave height (H). This method has a high accuracy of estimating wave period (T) in both wind
            and swell-generated seas (root mean square error = 0.76 s).

            Remya et al., 2010: Altimeter-derived ocean wave period using genetic algorithm - IEEE Geoscience and Remote Sensing Letters 8(2), 354–358. 61, 62, 100.

        Args:
            H (numpy array): significant wave height in metres
            U (numpy array): surface wind speed in metres per second
            grav (float): acceleration of gravity (m/s2) [default: 9.80665]

        Returns:
            period (numpy array): wave period following Remya et al. (2010) algorithm (second)
        """

        # Compute wave age
        eps = self._waveAge(H, U, grav=9.80665)

        # Wave age is then used in a Genetic Algorithm to obtain wave period
        period= (((eps-(5.78))/(eps+(U/(H*((U/H)+H)))))+(H+(5.70)))

        return period

    def meanEnergy(self, H, grav=9.80665, seadensity=1025.):
        """
        In a sea state, the average(mean) energy density per unit area of gravity waves on the water surface is proportional
        to the wave height squared, according to linear wave theory [Goda 2000].

        Method:
            Goda Y., 2000: Random Seas and Design of Maritime Structures - World Scientific, ISBN 978-981-02-3256-6.

            Holthuijsen L.H., 2007: Waves in oceanic and coastal waters - Cambridge: Cambridge University Press, ISBN 978-0-521-86028-4.

        Args:
            H (numpy array): significant wave height in metres
            grav (float): acceleration of gravity (m/s2) [default: 9.80665]
            seadensity (float): sea density (kg/m3) [default: 1025.]

        Returns:
            E (numpy array): average(mean) energy density per unit area of gravity waves (J/m2)
        """

        x = 1./8.
        h2 = np.square(H)
        E = x*seadensity * grav * h2

        return E

    def waveGroupVelocity(self, T, grav=9.80665):
        '''
        As the waves propagate, their energy is transported and the energy transport velocity is the group velocity.
        From Airy wave theory, the group velocity (cg) is calculated in (m/s).

        Args:
            T (numpy array): wave period in seconds
            grav (float): acceleration of gravity (m/s2) [default: 9.80665]

        Returns:
            cg (numpy array): group velocity (m/s)
        '''

        pi2 = 2*math.pi
        cg = grav * T / pi2

        return cg

    def waveEnergyFlux(self, H, T, grav=9.80665, seadensity=1025.):
        """
        The rate at which energy is carried by waves is determined using total wave energy and wave energy speed (kW/m)

        Args:
            H (numpy array): significant wave height in metres
            T (numpy array): wave period in seconds
            grav (float): acceleration of gravity (m/s2) [default: 9.80665]
            seadensity (float): sea density (kg/m3) [default: 1025.]

        Returns:
            P (numpy array): wave energy flux (kW/m)
        """

        E = self.meanEnergy(H, grav=9.80665, seadensity=1025.)
        cg = self.waveGroupVelocity(T, grav=9.80665)

        # convert from W/m to kW/m
        P = 0.001 * cg * E

        return P

    def timeSeries(self):
        """
        Time series of wave characteristics are obtained via both the significant wave height and wind speed parameters from the altimeter dataset.

        Time series compute the following **instantaneous** and **monthly** variables:

            * significant wave height (m) 'wh' & 'wh_rolling'
            * wave period (s)  'period' & 'period_rolling'
            * wave energy flux (kW/m)  'power' & 'power_rolling'
            * wave average energy density (J/m2)  'energy' & 'energy_rolling'
            * wave group velocity (m/s)  'speed' & 'speed_rolling'

        Note:
            The class **waveAnalysis()** saves a pandas dataframe called **timeseries** that stores the wave time series
            for further analysis.
        """
        # Compute wave parameters
        self.T = self.wavePeriod(self.wh, self.ws)
        self.we = self.meanEnergy(self.wh)
        self.speed = self.waveGroupVelocity(self.T)
        self.power1 = self.waveEnergyFlux(self.wh, self.T)

        sort_time = netCDF4.num2date(self.times, self.time_units)

        wavedf = pd.DataFrame(data={"date": sort_time, "wh":self.wh, "period":self.T, "energy":self.we,
                                "speed":self.speed, "power":self.power1, "lon":self.lon, "lat":self.lat})

        # 30 days averaged parameters.
        meanwave = wavedf.rolling('30D', on = 'date', min_periods = 1).mean()

        self.wh_rolling = meanwave['wh']
        self.period_rolling = meanwave['period']
        self.power_rolling = meanwave['power']
        self.speed_rolling = meanwave['speed']
        self.energy_rolling = meanwave['energy']

        self.timeseries = pd.DataFrame(data={"date": sort_time, "wh":self.wh, "wh_rolling":self.wh_rolling,
                                        "period":self.T, "period_rolling":self.period_rolling,
                                        "power":self.power1, "power_rolling":self.power_rolling,
                                        "energy":self.we, "energy_rolling":self.energy_rolling,
                                        "speed":self.speed, "speed_rolling":self.speed_rolling,
                                        "lat":self.lat, "lon":self.lon})

        self.timeseries['day'] = self.timeseries['date'].dt.day
        self.timeseries['month'] = self.timeseries['date'].dt.month
        self.timeseries['year'] = self.timeseries['date'].dt.year

        return

    def plotTimeSeries(self, time='all', series='H', fsize=(12, 5), fsave=None):
        """
        This function **plots** and **saves** in a figure a time series for a specific parameter from the processed altimeter data.
        It also provides the following information:

            * Maximum parameter value
            * Mean parameter value
            * Median parameter value
            * 95th percentile parameter value

        Args:
            time (list): extent of years to plot for plotting time series from 1995 to 2010 user will set 'time' to [1995,2010], to plot the entire record use the keyword 'all' [default: 'all']
            series (str): name of the series to plot choices are: 'H', 'T', 'P', 'E' and 'Cg' [default: 'H']
            fsize : size of the image [default: (12,5)]
            fsave (str): saved image name without extension that will be written as a PNG file [default: None]
        """

        if time == 'all':
            tmpdf = self.timeseries.copy()
        else:
            tmpdf = self.timeseries.copy()
            tmpdf = tmpdf[(tmpdf['date'].dt.year > time[0]) & (tmpdf['date'].dt.year < time[1])]

        if series == 'H':
            fig, ax1 = plt.subplots(figsize=fsize)
            ax1.plot(tmpdf.date,tmpdf.wh,color='lightgrey',label="wave height $H_s$")
            ax1.plot(tmpdf.date,tmpdf.wh_rolling,color='blue',label="30-Day Average $H_s$")

            ax1.legend(labels=["wave height $H_s$","30-Day Average $H_s$"], loc='upper left')
            ax1.set_ylabel("H$_s$ (m)",style = 'italic', fontsize=12)

            print ('Max wave height: {:0.3f} m'.format(max(tmpdf.wh)))
            print ('Mean wave height: {:0.3f} m'.format(np.mean(tmpdf.wh)))
            print ('Median wave height: {:0.3f} m'.format(np.median(tmpdf.wh)))
            print ('95th percentile wave height: {:0.3f} m'.format(np.percentile(tmpdf.wh,95)))

        elif series == 'T':
            fig, ax1 = plt.subplots(figsize=fsize)
            ax1.plot(tmpdf.date,tmpdf.period,color='lightgrey',label="wave period T$_\mathit{z}$")
            ax1.plot(tmpdf.date,tmpdf.period_rolling,color='blue',label="30-Day Average $H_s$")

            ax1.legend(labels=['wave period T$_\mathit{z}$',"30-Day Average T$_\mathit{z}$"], loc='upper left')
            ax1.set_ylabel("T$_\mathit{z}$ (s)",style = 'italic', fontsize=12)

            print ('Max wave period: {:0.3f} s'.format(max(tmpdf.period)))
            print ('Mean wave period: {:0.3f} s'.format(np.mean(tmpdf.period)))
            print ('Median wave period: {:0.3f} s'.format(np.median(tmpdf.period)))
            print ('95th percentile wave period: {:0.3f} s'.format(np.percentile(tmpdf.period,95)))

        elif series == 'P':
            fig, ax1 = plt.subplots(figsize=fsize)
            ax1.plot(tmpdf.date,tmpdf.power,color='lightgrey',label="wave power P")
            ax1.plot(tmpdf.date,tmpdf.power_rolling,color='blue',label="30-Day Average $\mathit{P}$")

            ax1.legend(labels=['wave power $\mathit{P}$',"30-Day Average $\mathit{P}$"], loc='upper left')
            ax1.set_ylabel("P (kW/m)",style = 'italic', fontsize=12)

            print ('Max wave power: {:0.3f} kW/m'.format(max(tmpdf.power)))
            print ('Mean wave power: {:0.3f} kW/m'.format(np.mean(tmpdf.power)))
            print ('Median wave power: {:0.3f} kW/m'.format(np.median(tmpdf.power)))
            print ('95th percentile wave power: {:0.3f} kW/m'.format(np.percentile(tmpdf.power,95)))

        elif series == 'Cg':
            fig, ax1 = plt.subplots(figsize=fsize)
            ax1.plot(tmpdf.date,tmpdf.speed,color='lightgrey',label="wave celerity $\mathit{C}$")
            ax1.plot(tmpdf.date,tmpdf.speed_rolling,color='blue',label="30-Day Average $\mathit{C}$")

            ax1.legend(labels=['wave celerity $\mathit{C}$',"30-Day Average $\mathit{C}$"], loc='upper left')
            ax1.set_ylabel("C (m/s)",style = 'italic', fontsize=12)

            print ('Max wave celerity: {:0.3f} m/s'.format(max(tmpdf.speed)))
            print ('Mean wave celerity: {:0.3f} m/s'.format(np.mean(tmpdf.speed)))
            print ('Median wave celerity: {:0.3f} m/s'.format(np.median(tmpdf.speed)))
            print ('95th percentile wave celerity: {:0.3f} m/s'.format(np.percentile(tmpdf.speed,95)))

        elif series == 'E':
            fig, ax1 = plt.subplots(figsize=fsize)
            ax1.plot(tmpdf.date,tmpdf.energy,color='lightgrey',label="wave energy $\mathit{E}$")
            ax1.plot(tmpdf.date,tmpdf.energy_rolling,color='blue',label="30-Day Average $\mathit{E}$")

            ax1.legend(labels=['wave energy $\mathit{E}$',"30-Day Average $\mathit{E}$"], loc='upper left')
            ax1.set_ylabel("E (J/m$^2$)",style = 'italic', fontsize=12)

            print ('Max wave energy: {:0.3f} J/m2'.format(max(tmpdf.energy)))
            print ('Mean wave energy: {:0.3f} J/m2'.format(np.mean(tmpdf.energy)))
            print ('Median wave energy: {:0.3f} J/m2'.format(np.median(tmpdf.energy)))
            print ('95th percentile wave energy: {:0.3f} J/m2'.format(np.percentile(tmpdf.energy,95)))

        else:
            raise ValueError('Not recognised series... choices are H, P, T, Cg, E')

        ax1.set_xlim(min(tmpdf.date),max(tmpdf.date))
        ax1.set_xlabel("Year", fontsize=12)

        ax1.grid(True, linewidth=0.5, color='k', alpha=0.1, linestyle='-')
        ax1.tick_params(labelcolor='k', labelsize='medium', width=3)

        plt.show()

        if fsave is not None:
            fig.savefig(fsave, dpi=100)
            print('Figure saved: ',fsave)

        return

    def close2Track(self, radius=2., dtmax=6):
        """
        From all cyclone tracks, this function finds the closest processed altimeter geographical locations that have been recorded in the database.
        In addition to their coordinates, the altimeter dataset has to be recorded during a user defined time lapse close enough to the cyclone path time
        at each position.

        The recorded dataframe **cyclone_data** contains the following variables:

            * altimeter significant wave height (m) 'wH'
            * altimeter wave period (s)  'period'
            * altimeter wave energy flux (kW/m)  'power'
            * altimeter wave average energy density (J/m2)  'energy'
            * altimeter wave group velocity (m/s)  'speed'
            * distance between altimeter coordinates and cyclone path (km)  'dist'
            * cyclone date (datetime)  'cdate'
            * difference in time between recorded cyclone date and altimeter data for specific position (hours)  'hours'
            * cyclone latitude position  'clat'
            * cyclone longitude position  'clon'
            * altimeter data latitude position  'lat'
            * altimeter data longitude position  'lon'

        Args:
            radius (float): maximum radius distance in degree between cyclone position and altimeter data coordinates [default: '2.']
            dtmax (float): maximum difference in time between recorded cyclone date and picked altimeter data (hours) [default: '6.']

        Note:
            The class **waveAnalysis()** saves a pandas dataframe called **cyclone_data** that stores the closest points to each cyclone path coordinates
            for further analysis.
        """

        if self.cyclone is None:
            raise ValueError('There is no cyclone path loaded in the class, this needs to be done during the class initialisation...')

        # Get altimeter positions
        XY = np.zeros((self.timeseries.shape[0],2))
        XY[:,0] = self.timeseries['lon'].to_numpy()
        XY[:,1] = self.timeseries['lat'].to_numpy()

        # Get cyclone positions
        cXY = np.zeros((self.cyclone.shape[0],2))
        cXY[:,0] = self.cyclone['lon'].to_numpy()
        cXY[:,1] = self.cyclone['lat'].to_numpy()

        # Search for closest altimeter points to cyclone track
        tree = _cKDTree(XY)
        pts = tree.query_ball_point(cXY, r=radius)

        # Get the ones that are in the right time interval...
        clon = []
        clat = []
        aT = []
        aC = []
        aP = []
        aE = []
        aH = []
        alat = []
        alon = []
        cdate = []
        difft = []
        dist = []

        for k in range(len(pts)):
            ngbhs = len(pts[k])
            if ngbhs>0:
                for p in range(ngbhs):
                    delta_time = self.timeseries.date.iloc[pts[k][p]] - self.cyclone.datetime.iloc[k].replace(tzinfo=None)
                    dhours = delta_time.total_seconds()/3600.
                    if abs(dhours)<dtmax:
                        difft.append(round(dhours, 3))
                        clon.append(cXY[k,0])
                        clat.append(cXY[k,1])
                        cdate.append(self.cyclone['datetime'].iloc[k])
                        d = geopy.distance.geodesic((cXY[k,1],cXY[k,0]), (self.timeseries['lat'].iloc[pts[k][p]],self.timeseries['lon'].iloc[pts[k][p]])).km
                        dist.append(round(d,3))
                        aT.append(self.timeseries['period'].iloc[pts[k][p]])
                        aC.append(self.timeseries['speed'].iloc[pts[k][p]])
                        aP.append(self.timeseries['power'].iloc[pts[k][p]])
                        aE.append(self.timeseries['energy'].iloc[pts[k][p]])
                        aH.append(self.timeseries['wh'].iloc[pts[k][p]])
                        alat.append(self.timeseries['lat'].iloc[pts[k][p]])
                        alon.append(self.timeseries['lon'].iloc[pts[k][p]])

        data = {'period': aT,
                'speed': aC,
                'power': aP,
                'energy': aC,
                'dist': dist,
                'date': cdate,
                'wH': aH,
                'lon': alon,
                'lat': alat,
                'clon': clon,
                'clat': clat,
                'hours': difft}
        self.cyclone_data = pd.DataFrame(data)

        return

    def cycloneAltiPoint(self, showinfo=False, extent=None, addcity=None, markersize=100, zoom=4, fsize=(12, 10)):
        """
        This function **plots** a series of figures of the geographical coordinates for processed altimeter data close to each cyclone path position.

        Args:
            showinfo (bool): show considered cyclone path coordiantes and associated recorded time and associate wave parameters [default: False]
            extent (int): geographical extent of the figure following the convention [lon min,lon max,lat min,lat max]  [default: None]
            addcity (list): defined a specific location using the following convention ['City Name', longitude, latitude] [default: None]
            markersize (int): size of the markers used to specify cyclone tracks [default: 100]
            zoom (int): given target zoom for the target domain background (must be a value >= 1) [default: 4]
            fsize : size of the image [default: (12,10)]

        Note:
            This function relies on **cartopy** and **matplotlib** libraries. We use cartopy’s ability to draw map tiles which are downloaded on demand
            from the **Stamen tile server**.

        Todo:
            There are some plotting problems for dataset spanning beyond the 180 degree meridian that will need to be fixed.
        """

        if self.cyclone is None:
            raise ValueError('There is no cyclone path loaded in the class, this needs to be done during the class initialisation...')

        if self.cyclone_data is None:
            raise ValueError('There is no altimeter data defined based on cyclone path, you need to run the close2Track(radius=2., dtmax=6) function before.')

        # Create a Stamen terrain background instance.
        stamen_terrain = cimgt.Stamen('terrain-background')
        unill = self.cyclone_data[['clat','clon','date']]
        unill = unill.drop_duplicates()

        # Loop over recorded cyclone path position
        for p in range(unill.shape[0]):

            cyclons = unill.clon.iloc[p]
            cyclats = unill.clat.iloc[p]

            if showinfo:
                print(' ')
                print('++++++++++++++++++++++++++++++++++++++++++++')
                print('')
                print('Considered cyclone path point ('+str(cyclons)+
                             ','+str(cyclats)+') at '+str(unill.date.iloc[p]))
                print('')
            fig = plt.figure(figsize=fsize)
            ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
            if extent is None:
                ax.set_extent([self.lonmin, self.lonmax, self.latmin, self.latmax], crs=ccrs.Geodetic())
            else:
                ax.set_extent([extent[0], extent[1], extent[2], extent[3]], crs=ccrs.Geodetic())

            ax.add_image(stamen_terrain, zoom)
            ax.coastlines(resolution='10m')

            geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
            text_transform = offset_copy(geodetic_transform, units='dots', x=-12)

            # Cyclone track
            clon = self.cyclone['lon'].to_numpy()
            clat = self.cyclone['lat'].to_numpy()
            for k in range(len(clon)-1):
                plt.plot([clon[k],clon[k+1]], [clat[k],clat[k+1]],
                     color='k', linewidth=1, alpha=1.,
                     transform=ccrs.PlateCarree(), zorder=1)
            plt.scatter([clon],[clat], marker='o', color='w', s=markersize*0.5, edgecolor='black', linewidth='0.5',
                    alpha=1, transform=ccrs.PlateCarree(), zorder=5)

            cycdata = self.cyclone_data
            ax.set_title('Altimeter data close to cyclone path point ('+str(cyclons)+
                         ','+str(cyclats)+') at '+str(unill.date.iloc[p]))
            plt.scatter(cyclons,cyclats, marker='o', s=markersize*3, color='k', edgecolor='black', linewidth='1',
                alpha=1, transform=ccrs.PlateCarree(), zorder=5)

            for k in range(cycdata.shape[0]):
                if cycdata.clon[k] == cyclons:
                    if cycdata.clat[k] == cyclats:
                        plt.scatter(cycdata.lon[k],cycdata.lat[k], marker='o', s=markersize*2, edgecolor='k', linewidth='1',
                            alpha=1, transform=ccrs.PlateCarree(), zorder=5)

            # Add a marker for a given city.
            if addcity is not None:
                name_city = addcity[0]
                lon_city = addcity[1]
                lat_city = addcity[2]
                ax.scatter(lon_city, lat_city, marker='o', color='navy', s=100, edgecolor='black', linewidth='0.5',
                        alpha=0.7, transform=ccrs.Geodetic())
                ax.text(lon_city, lat_city, name_city,
                            verticalalignment='center', horizontalalignment='right',
                            transform=text_transform,
                            bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'))

            d = geopy.distance.geodesic((cycdata.clat[0],cycdata.clon[0]),
                                        (cycdata.clat[0]+2.,cycdata.clon[0])).km
            d = round(d,3)*1.5

            circle_points = cartopy.geodesic.Geodesic().circle(lon=cyclons, lat=cyclats,
                                                               radius=d*1000., n_samples=100,
                                                               endpoint=False)
            geom = shapely.geometry.Polygon(circle_points)
            ax.add_geometries((geom,), crs=cartopy.crs.PlateCarree(), facecolor='None' ,
                              edgecolor='k', linewidth=1.5, zorder=31)

            gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                              linewidth=0.5, color='k', alpha=0.5, linestyle='--')
            gl.xlabels_top = False
            gl.ylabels_left = False
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER

            plt.show()

            if showinfo:
                cycdata = self.cyclone_data
                cyclons = unill.clon.iloc[p]
                cyclats = unill.clat.iloc[p]
                for k in range(cycdata.shape[0]):
                    if cycdata.clon[k] == cyclons:
                        if cycdata.clat[k] == cyclats:
                            print('Altimeter point ('+str(round(cycdata.lon[k],1))+
                                 ','+str(round(cycdata.lat[k],1))+') records dt: '+str(round(cycdata.hours[k],2))+'h')
                            print('    +    Power ',round(cycdata.power[k],2),'kW/m')
                            print('    +   Energy ',round(cycdata.energy[k],2),'J/m2')
                            print('    + Celerity ',round(cycdata.speed[k],2),'m/s')
                            print('    +   Period ',round(cycdata.period[k],2),'s')
                            print('    +   Height ',round(cycdata.wH[k],2),'m')
                            print(' ')

        return

    def seriesSeasonMonth(self, series='wh', time=None, lonlat=None, fsave=None, plot=True):
        """
        This function allows to analyse the seasonal characteristics of each parameter obtained from the altimeter dataset.
        For a specified time interval and geographical extent, it computes for a given wave variable the monthly seasonality.
        Obtained monthly averaged values are stored and returned with a Pandas dataframe. User has the option to plot the computed
        wave paraneter characteristics as a heatmap, a box plot and a standard deviation graph.

        For the wave height series, a Seasonal Mann-Kendall test is also performed to determine monotonic trends in computed dataset using the package from
        Hussain & Mahmud (2019).

        Hussain & Mahmud, 2019: pyMannKendall: a python package for non parametric Mann Kendall family of trend tests - JOSS, 4(39), 1556.

        Note:
            This function uses the seaborn and matplotlib libraries to plot the *heatmap* and the seasonal *boxplot*.

        Args:
            series (str): name of the series to plot based on **timeseries** dataframe, choices are: 'wh', 'period', 'power', 'energy' and 'speed' [default: 'wh']
            time (list): extent of years to plot for plotting time series from 1995 to 2010 user will set 'time' to [1995,2010] [default: None]
            lonlat (list): specifying the geographical extent of the season characteristics computation following the convention [lon min,lon max,lat min,lat max]  [default: None]
            fsave (str): saved image name without extension that will be written as a PNG file [default: None]
            plot (bool): flag specifying if plots have to been done [plot: True]

        Returns:
            dfseason (dataframe): pandas dataframe containing for chosen series variable the seasonality parameter for specified time interval
        """

        if self.timeseries is None:
            raise ValueError('The time series dataframe does not exist, you need to run the **timeSeries()** function first.')

        if lonlat is not None:
            # latitude and longitude
            if lonlat[0]>lonlat[1]:
                raise ValueError('Error wrong definition of min and max longitude in lonlat')
            if lonlat[2]>=lonlat[3]:
                raise ValueError('Error wrong definition of min and max latitude in lonlat')
            tdf = self.timeseries.drop(self.timeseries[self.timeseries.lon < lonlat[0]].index)
            tdf = tdf.drop(tdf[tdf.lon > lonlat[1]].index)
            tdf = tdf.drop(tdf[tdf.lat < lonlat[2]].index)
            tdf = tdf.drop(tdf[tdf.lat > lonlat[3]].index)
            tdf = tdf.groupby(['year', 'month'])[[series]].apply(np.mean).reset_index()
        else:
            tdf = self.timeseries.groupby(['year', 'month'])[[series]].apply(np.mean).reset_index()

        dftmp = tdf.drop(tdf[tdf.year < time[0]].index)
        dftmp = dftmp.drop(dftmp[dftmp.year > time[1]].index)

        dfseason = dftmp.pivot(index='year',columns='month',values=series)

        dfseason = dfseason.rename(columns={1: "January", 2: "February",
                              3: "March", 4: "April",
                              5: "May", 6: "June",
                              7: "July", 8: "August",
                              9: "September", 10: "October",
                              11: "November", 12: "December"})

        if plot:
            fig, ax = plt.subplots(figsize = (8,8))
            sns.heatmap(dfseason, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=1, cbar=False)
            if series == 'wh':
                ax.set_title('Significant Wave Height (m)',fontsize = 12)
            if series == 'period':
                ax.set_title('Wave Period (s)',fontsize = 12)
            if series == 'power':
                ax.set_title('Wave Power (kW/m)',fontsize = 12)
            if series == 'energy':
                ax.set_title('Wave Energy (J/m2)',fontsize = 12)
            if series == 'speed':
                ax.set_title('Wave Speed (m/s)',fontsize = 12)
            ax.set_ylabel("Years",fontsize = 12)
            ax.set_xlabel('Months',fontsize = 11)
            ax.yaxis.set_tick_params(labelsize=10)
            ax.xaxis.set_tick_params(labelsize=10, rotation=45)
            plt.tight_layout()
            plt.show()
            if fsave is not None:
                fig.savefig(fsave+'_'+series+'_heatmap', dpi=100)
                print('Figure saved: ',fsave+'_'+series+'_heatmap')

            fig, ax = plt.subplots(figsize = (8,5))
            sns.boxplot(data = dfseason, palette='Spectral')
            ax.set_title('Monthly distributions for chosen time interval',fontsize = 12)
            if series == 'wh':
                ax.set_ylabel('Significant Wave Height (m)',fontsize = 12)
            if series == 'period':
                ax.set_ylabel('Wave Period (s)',fontsize = 12)
            if series == 'power':
                ax.set_ylabel('Wave Power (kW/m)',fontsize = 12)
            if series == 'energy':
                ax.set_ylabel('Wave Energy (J/m2)',fontsize = 12)
            if series == 'speed':
                ax.set_ylabel('Wave Speed (m/s)',fontsize = 12)
            ax.set_xlabel('Months',fontsize = 11)
            ax.yaxis.set_tick_params(labelsize=10)
            ax.xaxis.set_tick_params(labelsize=10, rotation=45)
            plt.tight_layout()
            plt.show()
            if fsave is not None:
                fig.savefig(fsave+'_'+series+'_distribution', dpi=100)
                print('Figure saved: ',fsave+'_'+series+'_distribution')

            monthly_sd = dfseason.std(axis=0)
            fig, ax = plt.subplots(figsize = (8,4))
            monthly_sd.plot(color='blue', marker='o', linestyle='dashed', linewidth=2, markersize=12)
            if series == 'wh':
                ax.set_title('Standard deviation in significant wave height for chosen time interval',fontsize = 12)
            if series == 'period':
                ax.set_title('Standard deviation in wave period for chosen time interval',fontsize = 12)
            if series == 'power':
                ax.set_title('Standard deviation in wave power for chosen time interval',fontsize = 12)
            if series == 'energy':
                ax.set_title('Standard deviation in wave energy for chosen time interval',fontsize = 12)
            if series == 'speed':
                ax.set_title('Standard deviation in wave speed for chosen time interval',fontsize = 12)
            ax.set_ylabel("Standard deviation",fontsize = 12)
            ax.set_xlabel('Months',fontsize = 11)
            ax.yaxis.set_tick_params(labelsize=10)
            ax.xaxis.set_tick_params(labelsize=10, rotation=45)
            plt.tight_layout()
            plt.show()
            if fsave is not None:
                fig.savefig(fsave+'_'+series+'_sd', dpi=100)
                print('Figure saved: ',fsave+'_'+series+'_sd')

            if series == 'wh':
                wh_stack = dfseason.stack()
                seasonal_trend = mk.seasonal_test(wh_stack, period=12)
                print(' ')
                print('Change in yearly wave height trend accounting for seasonality:')
                print('    +           trend: ',seasonal_trend.trend)
                print('    +    slope (cm/y): ',str(round(seasonal_trend.slope*100., 2)))


        dfseason['mean'] = dfseason.mean(axis=1)

        return dfseason
