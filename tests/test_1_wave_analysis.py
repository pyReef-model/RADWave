import pytest
import RADWave

def test_waveAnalysis_class_building():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 153.0, -36.0, -35.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )

    satName = ['JASON-2', 'ENVISAT', 'TOPEX']
    assert wclass.satNb == 10, "test failed because satellites number equals " + str(wclass.satNb) + " instead of 10."
    assert wclass.nameSat == satName, "test failed because satellites names missmatch "

def test_altimeter_processing():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 155.0, -36.0, -34.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )

    wclass.processAltimeterData(altimeter_pick='all', saveCSV = 'altimeterData.csv')
    assert pytest.approx(wclass.wh.mean(),rel=1e-3) == 2.386, "test failed because extracted mean wave height missmatch"
    assert pytest.approx(wclass.ws.mean(),rel=1e-3) == 8.221, "test failed because extracted mean wind speed missmatch"

def test_timeseries_generation():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 155.0, -36.0, -34.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )

    wclass.readAltimeterData(saveCSV = 'altimeterData.csv')
    ts = wclass.generateTimeSeries(days=30)

    assert pytest.approx(ts['power'].mean(),rel=1e-3) == 87.752, "test failed"
    assert pytest.approx(ts['wh_rolling'].min(),rel=1e-3) == 1.208, "test failed"
    assert pytest.approx(ts['period_rolling'].max(),rel=1e-3) == 8.028, "test failed"

def test_wave_energy_flux():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 153.0, -36.0, -35.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )
    H = 15.5
    T = 10.
    P = wclass.waveEnergyFlux(H, T, grav=9.80665, seadensity=1025.0)
    assert pytest.approx(P,rel=1e-3) == 4711.495, "test failed"

def test_wave_group_velocity():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 153.0, -36.0, -35.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )
    T = 10.
    Cg = wclass.waveGroupVelocity(T, grav=9.80665)
    assert pytest.approx(Cg,rel=1e-3) == 15.608, "test failed"

def test_wave_mean_energy():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 153.0, -36.0, -35.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )
    H = 15.5
    mE = wclass.meanEnergy(H, grav=9.80665, seadensity=1025.0)
    assert pytest.approx(mE,rel=1e-3) == 301868.607, "test failed"

def test_wave_period():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 153.0, -36.0, -35.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )
    H = 15.5
    U = 25.1
    wP = wclass.wavePeriod(H, U, grav=9.80665)
    assert pytest.approx(wP,rel=1e-3) == 18.122, "test failed"

def test_seasonal_characteristics():

    wclass = RADWave.waveAnalysis(altimeterURL='tests/testURLs.txt',
                                  bbox=[152.0, 155.0, -36.0, -34.0],
                                  stime=[1998, 1, 1],
                                  etime=[2008, 12, 31]
                                 )

    wclass.readAltimeterData(saveCSV = 'altimeterData.csv')
    ts = wclass.generateTimeSeries(days=30)
    wh_season = wclass.computeSeasonalCharacteristics(series='wh', time=[1998,2008],
                                                      lonlat=None, fsave=None,
                                                      plot=False
                                                     )

    assert pytest.approx(wh_season['January'].mean(),rel=1e-3) == 2.143, "test failed"
    assert pytest.approx(wh_season['May'].min(),rel=1e-3) == 1.021, "test failed"
    assert pytest.approx(wh_season['October'].max(),rel=1e-3) == 3.246, "test failed"
