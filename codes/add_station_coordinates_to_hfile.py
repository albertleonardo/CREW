
import sys
import h5py
import pandas as pd

from obspy.core import UTCDateTime as UT

#load the isc registry

stas = pd.read_csv('gmap-stations_2.txt',sep='|')

def get_station_info(example):
	net = example.attrs['network']
	sta = example.attrs['station']
	tdf= stas[stas[' Station ']==sta]
	# check the times
	starttime = example.attrs['trace_start_time']
	tdf = tdf[(tdf[' StartTime ']< starttime)]
	return tdf






fname = sys.argv[1]

f = h5py.File(fname,'r+')
data = f['data']

names = list(data.keys())

for name in names:
	example = data[name]
	tdf = get_station_info(example)
	example.attrs['station_longitude'] = tdf[:1][' Longitude '].to_numpy()[0]
	example.attrs['station_latitude'] = tdf[:1][' Latitude '].to_numpy()[0]
	example.attrs['station_elevation'] = tdf[:1][' Elevation '].to_numpy()[0]

f.close()


