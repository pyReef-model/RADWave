import pytest

def test_scipy_import():
    import scipy
    print("\t\t You have scipy version {}".format(scipy.__version__))

def test_cartopy_import():
    import cartopy
    import cartopy.geodesic
    import cartopy.crs as ccrs
    import cartopy.io.img_tiles as cimgt
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    print("\t\t You have cartopy version {}".format(cartopy.__version__))

def test_netCDF4_import():
    import netCDF4
    from netCDF4 import Dataset as NetCDFFile
    print("\t\t You have netCDF4 version {}".format(netCDF4.__version__))

def test_pymannkendall_import():
    import pymannkendall
    print("\t\t You have pymannkendall version {}".format(pymannkendall.__version__))

def test_seaborn_import():
    import seaborn
    print("\t\t You have seaborn version {}".format(seaborn.__version__))

def test_pandas_import():
    import pandas
    print("\t\t You have pandas version {}".format(pandas.__version__))

def test_shapely_import():
    import shapely
    from shapely.geometry.polygon import LinearRing
    print("\t\t You have shapely version {}".format(shapely.__version__))

def test_geopy_import():
    import geopy
    import geopy.distance
    print("\t\t You have geopy version {}".format(geopy.__version__))

def test_radwave_modules():
    import RADWave
    from RADWave import documentation
    from RADWave import waveAnalysis

def test_jupyter_available():
    from subprocess import check_output
    try:
        result = str(check_output(['which', 'jupyter']))[2:-3]
    except:
        print("Jupyter not installed")
        print("Jupyter is needed to run the example documentation")
