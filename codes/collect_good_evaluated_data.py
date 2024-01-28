

# take the evaluation based on model predictions, get the clean indices and the clean data and write to new files

import sys
import h5py
import glob
import skynet

import numpy as np

#e.g. evaluation_clean_safe_cleaned_000_crew.npz
fname=sys.argv[1]

files=np.load(fname)

names=files['t_names']
clean_indices=files['clean_indices']

dataname = fname.split('.')[0]+'.hdf5'
dataname = dataname[11:]
data=skynet.open(dataname)

# write the newfile
outname=fname.split('_')[4]+'_CREW.hdf5'
print('writing to ',outname)
hf = h5py.File(outname,'w')
g1 = hf.create_group('data')
clean_names=names[clean_indices]
print(len(clean_names),len(names),len(clean_names)/len(names))

for name in clean_names:
	data.copy(data[name],hf['/data'],name)
	#replace 0 arrival times with NaN
	tname = '/data/'+name
	if hf[tname].attrs['Pn_arrival_sample']==0:
		#print('changing to NaN')
		hf[tname].attrs['Pn_arrival_sample']='NaN'
	if hf[tname].attrs['Pg_arrival_sample']==0:
		hf[tname].attrs['Pg_arrival_sample']='NaN'
	if hf[tname].attrs['P_arrival_sample']==0:
		hf[tname].attrs['P_arrival_sample']='NaN'
	if hf[tname].attrs['Sn_arrival_sample']==0:
		hf[tname].attrs['Sn_arrival_sample']='NaN'
	if hf[tname].attrs['Sg_arrival_sample']==0:
		hf[tname].attrs['Sg_arrival_sample']='NaN'
	if hf[tname].attrs['S_arrival_sample']==0:
		hf[tname].attrs['S_arrival_sample']='NaN'
	# change the name of the attributes to be in seisbench format,
	# create the new and delete the old ones
	# delete unnecessary attributes, like the uncertainties

	hf[tname].attrs['station_network_code']   = hf[tname].attrs['network']
	hf[tname].attrs['station_code']           = hf[tname].attrs['station']
	hf[tname].attrs['station_latitude_deg']   = hf[tname].attrs['station_latitude']
	hf[tname].attrs['station_longitude_deg']  = hf[tname].attrs['station_longitude']
	hf[tname].attrs['station_elevation_m']    = hf[tname].attrs['station_elevation']
	hf[tname].attrs['source_longitude_deg']   = hf[tname].attrs['event_origin_longitude']
	hf[tname].attrs['source_latitude_deg']    = hf[tname].attrs['event_origin_latitude']
	hf[tname].attrs['source_depth_km']        = hf[tname].attrs['event_origin_depth']/1000 
	hf[tname].attrs['trace_category']         = hf[tname].attrs['event_type']
	hf[tname].attrs['source_id']              = hf[tname].attrs['event_origin_ID']
	hf[tname].attrs['source_magnitude']	  = hf[tname].attrs['magnitude']
	hf[tname].attrs['path_ep_distance_deg']   = hf[tname].attrs['distance']
	hf[tname].attrs['path_azimuth_deg']       = hf[tname].attrs['azimuth']
	hf[tname].attrs['path_takeoff_angle_deg'] = hf[tname].attrs['takeoff_angle']
	hf[tname].attrs['source_origin_time']     = hf[tname].attrs['event_origin_time']
	
	del hf[tname].attrs['event_origin_time']
	del hf[tname].attrs['takeoff_angle']
	del hf[tname].attrs['azimuth']
	del hf[tname].attrs['distance']
	del hf[tname].attrs['magnitude']
	del hf[tname].attrs['network']
	del hf[tname].attrs['station']
	del hf[tname].attrs['station_latitude']
	del hf[tname].attrs['station_longitude']
	del hf[tname].attrs['station_elevation']
	del hf[tname].attrs['event_origin_longitude']
	del hf[tname].attrs['event_origin_latitude']
	del hf[tname].attrs['event_origin_depth']
	del hf[tname].attrs['event_type']
	del hf[tname].attrs['event_origin_ID']
	del hf[tname].attrs['event_origin_depth_uncertainty']
	del hf[tname].attrs['event_origin_time_uncertainty']
	del hf[tname].attrs['event_origin_longitude_uncertainty']
	del hf[tname].attrs['event_origin_latitude_uncertainty']
	del hf[tname].attrs['P_weight']
	del hf[tname].attrs['Pn_weight']
	del hf[tname].attrs['Pg_weight']
	del hf[tname].attrs['S_weight']
	del hf[tname].attrs['Sn_weight']
	del hf[tname].attrs['Sg_weight']
	del hf[tname].attrs['P_evaluation_mode']
	del hf[tname].attrs['Pn_evaluation_mode']
	del hf[tname].attrs['Pg_evaluation_mode']
	del hf[tname].attrs['S_evaluation_mode']
	del hf[tname].attrs['Sn_evaluation_mode']
	del hf[tname].attrs['Sg_evaluation_mode']


hf.close()












