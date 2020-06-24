import pytest
import RADWave


def test_trackCyclone_class_building():

    cyc = RADWave.waveAnalysis(
        altimeterURL="tests/IMOS_YASI.txt",
        bbox=[170, 175, -17, -12],
        stime=[2011, 1, 27],
        etime=[2011, 2, 4],
        cycloneCSV="tests/2010-YASI.csv",
    )

    assert round(cyc.cyclone["pressure"].mean(), 3) == 977.214, "test failed "
    assert cyc.cyclone["name"][0] == "YASI", "test failed "

    satName = ["JASON-2", "CRYOSAT-2", "ENVISAT"]
    assert cyc.satNb == 10, (
        "test failed because satellites number equals "
        + str(wclass.satNb)
        + " instead of 10."
    )
    assert cyc.nameSat == satName, "test failed because satellites names missmatch "


def test_cycloneAltimeter_processing():

    cyc = RADWave.waveAnalysis(
        altimeterURL="tests/IMOS_YASI.txt",
        bbox=[170, 175, -17, -12],
        stime=[2011, 1, 27],
        etime=[2011, 2, 4],
        cycloneCSV="tests/2010-YASI.csv",
    )

    # cyc.readAltimeterData(saveCSV="tests/altimeterData2.csv")
    cyc.processAltimeterData(
        max_qc=1, altimeter_pick="all", saveCSV="tests/altimeterData2.csv"
    )
    assert (
        pytest.approx(cyc.wh.mean(), rel=1e-3) == 2.292
    ), "test failed because extracted mean wave height missmatch"
    assert (
        pytest.approx(cyc.ws.mean(), rel=1e-3) == 8.002
    ), "test failed because extracted mean wind speed missmatch"


def test_cycloneTimeseries_generation():

    cyc = RADWave.waveAnalysis(
        altimeterURL="tests/IMOS_YASI.txt",
        bbox=[170, 175, -17, -12],
        stime=[2011, 1, 27],
        etime=[2011, 2, 4],
        cycloneCSV="tests/2010-YASI.csv",
    )
    cyc.readAltimeterData(saveCSV="tests/altimeterData2.csv")
    ts = cyc.generateTimeSeries(days=30)

    assert pytest.approx(ts["power"].mean(), rel=1e-3) == 68.851, "test failed"
    assert pytest.approx(ts["wh_rolling"].min(), rel=1e-3) == 1.676, "test failed"
    assert pytest.approx(ts["period_rolling"].max(), rel=1e-3) == 7.715, "test failed"


def test_cycloneTrack():

    cyc = RADWave.waveAnalysis(
        altimeterURL="tests/IMOS_YASI.txt",
        bbox=[170, 175, -17, -12],
        stime=[2011, 1, 27],
        etime=[2011, 2, 4],
        cycloneCSV="tests/2010-YASI.csv",
    )
    cyc.readAltimeterData(saveCSV="tests/altimeterData2.csv")
    ts = cyc.generateTimeSeries(days=30)
    track = cyc.close2Track(radius=2.0, dtmax=16.0)

    assert (
        pytest.approx(cyc.cyclone_data["period"].max(), rel=1e-3) == 7.863
    ), "test failed"
    assert (
        pytest.approx(cyc.cyclone_data["speed"].max(), rel=1e-3) == 12.272
    ), "test failed"
    assert pytest.approx(cyc.cyclone_data["wH"].max(), rel=1e-3) == 1.735, "test failed"
