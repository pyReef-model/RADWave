import pytest
import RADWave

def test_trackCyclone_class_building():

    cyc = RADWave.waveAnalysis(altimeterURL='tests/IMOS_YASI.txt',
                               bbox=[170, 175, -17, -12],
                               stime=[2011,1,27],
                               etime=[2011,2,4],
                               cycloneCSV='tests/2010-YASI.csv'
                              )

    assert round(cyc.cyclone['pressure'].mean(),3) == 977.214, "test failed "
    assert cyc.cyclone['name'][0] == 'YASI', "test failed "

    satName = ['JASON-2', 'CRYOSAT-2', 'ENVISAT']
    assert cyc.satNb == 10, "test failed because satellites number equals " + str(wclass.satNb) + " instead of 10."
    assert cyc.nameSat == satName, "test failed because satellites names missmatch "

def test_cycloneAltimeter_processing():

    cyc = RADWave.waveAnalysis(altimeterURL='tests/IMOS_YASI.txt',
                               bbox=[170, 175, -17, -12],
                               stime=[2011,1,27],
                               etime=[2011,2,4],
                               cycloneCSV='tests/2010-YASI.csv'
                              )

    cyc.processAltimeterData(altimeter_pick='all', saveCSV = 'altimeterData.csv')
    assert round(cyc.wh.mean(),3) == 2.292, "test failed because extracted mean wave height missmatch"
    assert round(cyc.ws.mean(),3) == 8.002, "test failed because extracted mean wind speed missmatch"

def test_cycloneTimeseries_generation():

    cyc = RADWave.waveAnalysis(altimeterURL='tests/IMOS_YASI.txt',
                               bbox=[170, 175, -17, -12],
                               stime=[2011,1,27],
                               etime=[2011,2,4],
                               cycloneCSV='tests/2010-YASI.csv'
                              )
    cyc.readAltimeterData(saveCSV = 'altimeterData.csv')
    ts = cyc.generate_time_series(days=30)

    assert round(ts['power'].mean(),3) == 68.851, "test failed"
    assert round(ts['wh_rolling'].min(),3) == 1.676, "test failed"
    assert round(ts['period_rolling'].max(),3) == 7.715, "test failed"

def test_cycloneTrack():

    cyc = RADWave.waveAnalysis(altimeterURL='tests/IMOS_YASI.txt',
                               bbox=[170, 175, -17, -12],
                               stime=[2011,1,27],
                               etime=[2011,2,4],
                               cycloneCSV='tests/2010-YASI.csv'
                              )
    cyc.readAltimeterData(saveCSV = 'altimeterData.csv')
    ts = cyc.generate_time_series(days=30)
    track = cyc.close2Track(radius=2.,dtmax=16.)

    assert round(cyc.cyclone_data['period'].max(),3) == 7.863, "test failed"
    assert round(cyc.cyclone_data['speed'].max(),3) == 12.272, "test failed"
    assert round(cyc.cyclone_data['wH'].max(),3) == 1.735, "test failed"
