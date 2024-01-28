

################################################################
# This version starts by reading the mseedfile and finding
# the corresponding metadata
################################################################

#
# latest fixes
#
# ensure both P and S picks are in the waveform, change to random_trim function. turned out to be better to write check_times function
#
#
# switch all the names to seisbench convention


import os
import sys
import h5py
import glob

import numpy as np
import pandas as pd

from obspy import read,Stream
from obspy.core import UTCDateTime as UT


def row_to_hdf(row,dataset):
	"""
	add an example from  to a h5py dataset
	"""
	
	# read the waveforms
	st = pair_data_waveforms(row)
	



def pair_data_waveforms(df):
	"""
	retrieves the waveform corresponding to the row in the dataframe, if it exists
	"""
	phases = identify_phases(df)
	phase = phases[0]
	df['wavenames'] = '??.'+df['station']+'.'+df[phase]+'.'+'*'+'.mseed'
	print(df['wavenames'])
	try:
		#st = read('/oak/stanford/schools/ees/beroza/aguilars/Pn/ehdf_mseedfiles/'+df['wavenames'])
		st = read('/oak/stanford/schools/ees/beroza/aguilars/Pn/isc_mseedfiles/'+df['wavenames'])
		return st
	except Exception as e:
		'No waveforms found'
	


def identify_phases(df):
	"""
	identifires which phase is the first one  and all available in a row
	"""
	phases = []
	if df['Pg']!='NaN': phases.append('Pg')
	if df['Pn']!='NaN': phases.append('Pn')
	if df['P']!='NaN': phases.append('P')
	if df['Sg']!='NaN': phases.append('Sg')
	if df['Sn']!='NaN': phases.append('Sn')
	if df['S']!='NaN': phases.append('S')


	return phases

def select_channel(st):
	"""
	returns only the channels that are closest to 100 Hz sampling rate
	"""
	sampling_rates = [tr.stats.sampling_rate for tr in st]
	sampling_rates = set(sampling_rates)
	
	
def partition_st(st):
	"""
	returns a list of obspy streams per instrument codes
	"""
	codes = set([tr.stats.channel[:2] for tr in st])
	locations = set([tr.stats.location for tr in st])
	sts   = []

	for code in codes:
		tst = st.select(channel=code+'?')
		locations = set([tr.stats.location for tr in tst])
		for location in locations:
			if len(tst.select(location=location))==3:
				sts.append(tst.select(location=location))

	return sts


def prepare_st(st):
	
	for tr in st:
		if tr.stats.sampling_rate < 5:
			st.remove(tr)
	if len(st)==0:
		return Stream()

	original_sampling_rates = [tr.stats.sampling_rate for tr in st]

	st = st.merge(fill_value='latest')

	#st = st.detrend('linear')
	st = st.detrend('demean')	
	

	initial_time = max([tr.stats.starttime for tr in st]) 
	# cutting at the max to avoid the zero padding at the beginning
	
	end_time     = max([tr.stats.endtime for tr in st])

	st = st.trim(starttime=initial_time,endtime=initial_time+360,pad=True,fill_value=0)
	st = st.resample(100)
	
	return st


def enforce_length(st,length):
	"""
	enforces a specified number of sample points for waveforms, at the beginning and at the end
	:param st: obspy.core.stream
	:param length: desired length of waveforms in seconds
	"""
	for tr in st:
		i=1

def check_times(metadata,st):
	"""
	checks that the picks are within the waveform window
	"""
	#times = [metadata.P, metadata.Pg, metadata.Pn, metadata.S, metadata.Sg, metadata.Sn]
	#times = [UT(time) for time in times]
	times = []
	if metadata['Pn']  != 'NaN':
		times.append(metadata.Pn)
	if metadata['P'] != 'NaN':
		times.append(metadata.P)
	if metadata['Pg']  != 'NaN':
		times.append(metadata.Pg)
	if metadata['S']  != 'NaN':
		times.append(metadata.S)
	if metadata['Sn']  != 'NaN':
		times.append(metadata.Sn)
	if metadata['Sg']  != 'NaN':
		times.append(metadata.Sg)

	times = [UT(time) for time in times]


	for time in times:
		if time < st[0].stats.starttime:
			return False
		if time > st[0].stats.endtime:
			return False
		else:
			return True

def pad_waveforms(st,length):
	"""
	pads the waveforms at both ends to desired length 
	:param st: obspy.core.stream
	:param length: desired length of waveforms in seconds
	"""
	# first pad to earliest starttime and latest endtime
	initial_time = min([tr.stats.starttime for tr in st])
	end_time     = max([tr.stats.endtime for tr in st])

	for tr in st:
		intial_pad = (tr.stats.starttime - initial_time)*tr.stats.sampling_rate
		end_pad    = (end_time - tr.stats.endtime)*tr.stats.sampling_rate
		# create the pads
	
def random_trim(st):
	"""
	takes the initially desired 6 minute long waveforms and cut a random 5 minute piece
	"""
	index = np.random.randint(low=0,high=3000)/100 # somewhere between 0 and 50 s
	st = st.trim(starttime = st[0].stats.starttime+index  ,endtime=st[0].stats.starttime+index+(5*60)-st[0].stats.delta)

	return st


def assemble_X(st):
	"""
	cast the traces of the obspy stream into a numpy array (matrix)
	"""
	data = np.zeros((3,30000))
	st   = st.sort() # to order the channels, E,N,Z or 1,2,Z

	for i,tr in enumerate(st):
		data[i,:] = tr.data[:30000]

	return data


def normalize_X(data):
	"""
	normalizes on a row basis 
	: observation : the output is in the range [0 1]
	it might be desired to standardize in  some cases
	"""

	data[0,:] = data[0,:] / (np.max(np.abs(data[0,:])))
	data[1,:] = data[1,:] / (np.max(np.abs(data[1,:])))
	data[2,:] = data[2,:] / (np.max(np.abs(data[2,:])))

	return data

#def process_waveforms(st):
	
def add_data_to_hdf(data,name,target_file):
	"""
	adds one matrix to the hdf file
	"""
	target_file.create_dataset(name,data=data)
	
	return target_file


def create_y_dic(metadata,st):
	
	
	tr        = st[0]
	starttime = tr.stats.starttime
	y_dic     = {'P':0,'S':0,'Pg':0,'Pn':0,'Sg':0,'Sn':0,'trace_start_time':str(starttime)}
	
	if metadata.P != 'NaN':
		y_dic['P'] = (UT(metadata.P) - tr.stats.starttime)*tr.stats.sampling_rate

	if metadata.Pg != 'NaN':
		y_dic['Pg'] = (UT(metadata.Pg) - tr.stats.starttime)*tr.stats.sampling_rate

	if metadata.Pn != 'NaN':
		y_dic['Pn'] = (UT(metadata.Pn) - tr.stats.starttime)*tr.stats.sampling_rate


	if metadata.S != 'NaN':
		y_dic['S'] = (UT(metadata.S) - tr.stats.starttime)*tr.stats.sampling_rate

	if metadata.Sg != 'NaN':
		y_dic['Sg'] = (UT(metadata.Sg) - tr.stats.starttime)*tr.stats.sampling_rate

	if metadata.Sn != 'NaN':
		y_dic['Sn'] = (UT(metadata.Sn) - tr.stats.starttime)*tr.stats.sampling_rate	
	return y_dic



def get_rms_amplitudes(X,y_dic,window_size=5):

	"""
	calcualtes the rms amplitude of the seismogram in a window around the arrivals
	and takes the mean over the channels
	takes y _dic from  function create_input
	"""
	if y_dic['P'] != 0:
		reference_p = 'P'
	if y_dic['Pg'] != 0:
		reference_p = 'Pg'
	if y_dic['Pn'] !=0:
		reference_p = 'Pn'

	if y_dic['S'] != 0:
		reference_s = 'S'
	if y_dic['Sg'] != 0:
		reference_s = 'Sg'
	if y_dic['Sn'] !=0:
		reference_s = 'Sn'


	noise_rms = 0
	p_rms     = 0
	s_rms     = 0

	wav_matrix = X

	try:
		noise_rms = np.sqrt(np.sum(wav_matrix[:,int(y_dic[reference_p]-int(window_size*100)):int(y_dic[reference_p])]**2))
	except Exception as e:
		noise_rms = 0
	try:
		p_rms     = np.sqrt(np.sum(wav_matrix[:,int(y_dic[reference_p]):int(y_dic[reference_p]+int(window_size*100))]**2))
	except Exception as e:
		p_rms = 0
	try:
		s_rms     = np.sqrt(np.sum(wav_matrix[:,int(y_dic[reference_s]):int(y_dic[reference_s]+int(window_size*100))]**2))
	except Exception as e:
		s_rms = 0


	rms_dic={'noise_rms':noise_rms,'P_rms':p_rms,'S_rms':s_rms}
	print(rms_dic)
	return rms_dic



def find_metadata(filename,df):
	"""
	finds the metadata corresponding to a given mseed file
	names have the following structure 
	1B.KARA.2006-07-14T13:17:53.100000Z.Pn.mseed
	# not anymore
	# year_network.station_originid.mseed 
	# 2006_1B.KARA_4673y73.mseed

	"""
	#phase   = filename.split('.')[-2]
	station = filename.split('.')[1]
	station = station.split('_')[0]
	oid     = filename.split('_')[2]
	oid     = 'origid='+oid.split('.')[0]
	#time    = filename.split('.')[2]+'.'+filename.split('.')[3] 
	print(station,oid)
	tdf = df[(df['origin_ID']==oid)&(df['station']==station)]

	return tdf



##################################################################################################################3
# Test with just one file from 2000

year = sys.argv[1]

df = pd.read_csv(year+'_all_isc.csv')
df = df.fillna('NaN')
print(df)
#df['wavenames'] = 

#df = df[df['station']=='AGPR']
df['distance'] = pd.Series(data=df['distance'],dtype=float)
df = df[(df['distance']>1)&(df['distance']<20)]
print(df)

hf = h5py.File(year+'_isc_mseed_data.hdf5','w')
g1 = hf.create_group('data')


j=0

mseedfilenames = glob.glob('/oak/stanford/schools/ees/beroza/aguilars/Pn/isc_mseedfiles/'+year+'_*.*_*.mseed')

print(len(mseedfilenames),' files to process')


for filename in mseedfilenames:
	tfilename = filename.split('/')[-1]
	# find the metadata
	print(filename)
	metadata = find_metadata(tfilename,df)
	#print(filename)
	#print(metadata)
	if len(metadata)==0:
		continue

	print(metadata)	
	row = metadata.iloc[0]

	st = read(filename)
	
	if st:
		print('continuing to process waveforms')
		#st = st.merge()
		st = prepare_st(st)
		print(st)
		#time_check = check_times(row,st)
		#if not time_check:
		#	continue

		if len(st)<3:
			print('not enough channels, onto the next one')
			continue

		p_st = partition_st(st)
		for t_st in p_st:
			t_st = random_trim(t_st)
			print(t_st)
			
			#time_check = check_times(row,t_st)
			#if not time_check:
			#	continue
			try:

				X       = assemble_X(t_st)
				X       = normalize_X(X)
				y_dic   = create_y_dic(row,t_st)		
				rms_dic = get_rms_amplitudes(X,y_dic=y_dic,window_size=5)

				#try:

				network  = t_st[0].stats.network; 
				station  = t_st[0].stats.station
				channels = [tr.stats.channel for tr in t_st]
				ref_chan = channels[0][:2]					
				location = t_st[0].stats.location

				#outname = network+'.'+station+'.'+ref_chan+'.'+str(st[0].stats.starttime)
				outname = network+'.'+station+'.'+ref_chan+'_'+str(row['origin_ID'])
				g1.create_dataset(outname,data=X)			
				
				g1[outname].attrs['network_code']  = network
				g1[outname].attrs['station_code']  = station
				g1[outname].attrs['channels'] = channels

				# in order to make the names reproducible, keep the time in the name
				# as the string that was used in download
				g1[outname].attrs['trace_start_time']= str(t_st[0].stats.starttime)

				g1[outname].attrs['P_arrival_time']    =row['P']
				g1[outname].attrs['Pg_arrival_time']   =row['Pg']
				g1[outname].attrs['Pn_arrival_time']   =row['Pn']
				g1[outname].attrs['S_arrival_time']    =row['S']
				g1[outname].attrs['Sg_arrival_time']   =row['Sg']
				g1[outname].attrs['Sn_arrival_time']   =row['Sn']
				g1[outname].attrs['P_arrival_sample']  =y_dic['P']
				g1[outname].attrs['Pg_arrival_sample'] =y_dic['Pg']
				g1[outname].attrs['Pn_arrival_sample'] =y_dic['Pn']
				g1[outname].attrs['S_arrival_sample']  =y_dic['S']
				g1[outname].attrs['Sg_arrival_sample'] =y_dic['Sg']
				g1[outname].attrs['Sn_arrival_sample'] =y_dic['Sn']

				g1[outname].attrs['P_weight']          =row['P_weight']
				g1[outname].attrs['Pg_weight']         =row['Pg_weight']
				g1[outname].attrs['Pn_weight']         =row['Pn_weight']
				g1[outname].attrs['S_weight']          =row['S_weight']
				g1[outname].attrs['Sg_weight']         =row['Sg_weight']
				g1[outname].attrs['Sn_weight']         =row['Sn_weight']
				g1[outname].attrs['P_evaluation_mode'] =row['P_evaluation_mode']
				g1[outname].attrs['Pg_evaluation_mode']=row['Pg_evaluation_mode']
				g1[outname].attrs['Pn_evaluation_mode']=row['Pn_evaluation_mode']
				g1[outname].attrs['S_evaluation_mode'] =row['S_evaluation_mode']
				g1[outname].attrs['Sg_evaluation_mode']=row['Sg_evaluation_mode']
				g1[outname].attrs['Sn_evaluation_mode']=row['Sn_evaluation_mode']



				g1[outname].attrs['event_origin_time']=row['origin_time']
				#g1[outname].attrs['event_origin_time_uncertainty']=row['origin_time_uncertainty']
				g1[outname].attrs['source_longitude_deg']=row['origin_longitude']
				#g1[outname].attrs['event_origin_longitude_uncertainty']=row['origin_longitude_uncertainty']
				g1[outname].attrs['source_latitude_deg']=row['origin_latitude']
				#g1[outname].attrs['event_origin_latitude_uncertainty']=row['origin_latitude_uncertainty']
				g1[outname].attrs['source_depth_km']=row['depth']
				#g1[outname].attrs['event_origin_depth_uncertainty']=row['depth_uncertainty']
				g1[outname].attrs['event_origin_ID']=row['origin_ID']
				g1[outname].attrs['distance']=row['distance']
				g1[outname].attrs['azimuth']=row['azimuth']
				g1[outname].attrs['takeoff_angle']=row['takeoff_angle']
				g1[outname].attrs['source_magnitude']=row['magnitude']
				g1[outname].attrs['event_type']=row['event_type']

				# amplitude attributes
				
				g1[outname].attrs['noise_rms']=rms_dic['noise_rms']
				g1[outname].attrs['p_rms']=rms_dic['P_rms']
				g1[outname].attrs['s_rms']=rms_dic['S_rms']


				j += 1	

			except Exception as e: print(e)							


	else:
		print('passing to next row')
		pass


hf.close()

# check source-receiver distance?
#       add_station_coordinates_to_hfile.py
# then  purify_data_from_wrong_stations.py







"""
for filename in mseedfilenames:
	tfilename = filename.split('/')[-1]
	# find the metadata
	print(filename)
	metadata = find_metadata(tfilename,df)
	#print(filename)
	#print(metadata)
	if len(metadata)==0:
		continue

	print(metadata)	
	row = metadata.iloc[0]

	st = read(filename)
	
	if st:
		print('continuing to process waveforms')
		#st = st.merge()
		st = prepare_st(st)
		print(st)
		#time_check = check_times(row,st)
		#if not time_check:
		#	continue

		if len(st)<3:
			print('not enough channels, onto the next one')
			continue

		p_st = partition_st(st)
		for t_st in p_st:
			t_st = random_trim(t_st)
			print(t_st)
			
			#time_check = check_times(row,t_st)
			#if not time_check:
			#	continue
			try:

				X       = assemble_X(t_st)
				X       = normalize_X(X)
				y_dic   = create_y_dic(row,t_st)		
				rms_dic = get_rms_amplitudes(X,y_dic=y_dic,window_size=5)

				#try:

				network  = t_st[0].stats.network; 
				station  = t_st[0].stats.station
				channels = [tr.stats.channel for tr in t_st]
				ref_chan = channels[0][:2]					
				location = t_st[0].stats.location

				#outname = network+'.'+station+'.'+ref_chan+'.'+str(st[0].stats.starttime)
				outname = network+'.'+station+'.'+ref_chan+'_'+str(row['origin_ID'])
				g1.create_dataset(outname,data=X)			
				
				g1[outname].attrs['network']  = network
				g1[outname].attrs['station']  = station
				g1[outname].attrs['channels'] = channels

				# in order to make the names reproducible, keep the time in the name
				# as the string that was used in download
				g1[outname].attrs['trace_start_time']= str(t_st[0].stats.starttime)

				g1[outname].attrs['P_arrival_time']    =row['P']
				g1[outname].attrs['Pg_arrival_time']   =row['Pg']
				g1[outname].attrs['Pn_arrival_time']   =row['Pn']
				g1[outname].attrs['S_arrival_time']    =row['S']
				g1[outname].attrs['Sg_arrival_time']   =row['Sg']
				g1[outname].attrs['Sn_arrival_time']   =row['Sn']
				g1[outname].attrs['P_arrival_sample']  =y_dic['P']
				g1[outname].attrs['Pg_arrival_sample'] =y_dic['Pg']
				g1[outname].attrs['Pn_arrival_sample'] =y_dic['Pn']
				g1[outname].attrs['S_arrival_sample']  =y_dic['S']
				g1[outname].attrs['Sg_arrival_sample'] =y_dic['Sg']
				g1[outname].attrs['Sn_arrival_sample'] =y_dic['Sn']



				g1[outname].attrs['P_weight']          =row['P_weight']
				g1[outname].attrs['Pg_weight']         =row['Pg_weight']
				g1[outname].attrs['Pn_weight']         =row['Pn_weight']
				g1[outname].attrs['S_weight']          =row['S_weight']
				g1[outname].attrs['Sg_weight']         =row['Sg_weight']
				g1[outname].attrs['Sn_weight']         =row['Sn_weight']
				g1[outname].attrs['P_evaluation_mode'] =row['P_evaluation_mode']
				g1[outname].attrs['Pg_evaluation_mode']=row['Pg_evaluation_mode']
				g1[outname].attrs['Pn_evaluation_mode']=row['Pn_evaluation_mode']
				g1[outname].attrs['S_evaluation_mode'] =row['S_evaluation_mode']
				g1[outname].attrs['Sg_evaluation_mode']=row['Sg_evaluation_mode']
				g1[outname].attrs['Sn_evaluation_mode']=row['Sn_evaluation_mode']



				g1[outname].attrs['event_origin_time']=row['origin_time']
				g1[outname].attrs['event_origin_time_uncertainty']=row['origin_time_uncertainty']
				g1[outname].attrs['event_origin_longitude']=row['origin_longitude']
				g1[outname].attrs['event_origin_longitude_uncertainty']=row['origin_longitude_uncertainty']
				g1[outname].attrs['event_origin_latitude']=row['origin_latitude']
				g1[outname].attrs['event_origin_latitude_uncertainty']=row['origin_latitude_uncertainty']
				g1[outname].attrs['event_origin_depth']=row['depth']
				g1[outname].attrs['event_origin_depth_uncertainty']=row['depth_uncertainty']
				g1[outname].attrs['event_origin_ID']=row['origin_ID']
				g1[outname].attrs['distance']=row['distance']
				g1[outname].attrs['azimuth']=row['azimuth']
				g1[outname].attrs['takeoff_angle']=row['takeoff_angle']
				g1[outname].attrs['magnitude']=row['magnitude']
				g1[outname].attrs['event_type']=row['event_type']

				# amplitude attributes
				
				g1[outname].attrs['noise_rms']=rms_dic['noise_rms']
				g1[outname].attrs['p_rms']=rms_dic['P_rms']
				g1[outname].attrs['s_rms']=rms_dic['S_rms']


				j += 1	

			except Exception as e: print(e)							


	else:
		print('passing to next row')
		pass


hf.close()
"""


# the end?


