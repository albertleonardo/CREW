
# there are multiple wrongly assigned waveforms, to the same station name, but different networks

import sys
import h5py
import skynet
import numpy as np
import pandas as np

from obspy.geodetics import calc_vincenty_inverse
def sanity_check_distance(example):
	distance,az,baz = calc_vincenty_inverse(example.attrs['event_origin_latitude'],example.attrs['event_origin_longitude'],
				    example.attrs['station_latitude'],example.attrs['station_longitude'])
	residual = abs(distance/111000 - example.attrs['distance'])
	#print(residual,distance/111000,example.attrs['distance'],example.attrs['station'],example.attrs['event_origin_ID'])
	if residual>1:
		print('wrong station')
		return False
	else:
		return True

fname=sys.argv[1]

data = skynet.open(fname)

outname = 'cleaned_'+fname
hf = h5py.File(outname,'w')
g1 = hf.create_group('data')

names = list(data.keys())
for name in names:
	example=data[name]
	check = sanity_check_distance(example)
	if check==True:
		if example.attrs['Pn_arrival_sample']>1000:
			data.copy(data[name],hf['/data'],name) 

hf.close()



