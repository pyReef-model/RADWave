# Running tests...
import RADWave as rwave
wa = rwave.waveAnalysis(altimeterURL='testURLs.txt', bbox=[152.0,155.0,-36.0,-34.0],
                  stime=[1985,1,1], etime=[2018,12,31], test=True)
wa.processingAltimeterData(altimeter_pick='all')
