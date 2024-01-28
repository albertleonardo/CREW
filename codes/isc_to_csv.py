
##########################################
#
# Takes an earthquake catalog and writes 
# a csv file contianing earthquake and 
# phase information, similar to STEAD format
#
##########################################
#
# log
#
# added the event_type column Sep 02 / 2021
#



import os
import sys
import glob
import numpy as np
import pandas as pd

#pd.set_option('display.max_columns', 22)

from obspy import read_events
from obspy.core import UTCDateTime as UT

filename = sys.argv[1]

def pair_picks_arrivals(ev,origin_index):
	"""
	function pair_pics_arrivals
	creates a list with tuples containing pick-arrival pairs
	:type  ev: obspy.core.event.event.Event
	:param ev:
	event to select picks and arrivals from
	:param origin_index:
	index of the origin that contains the arrivals

	example usage:
	>>> cat = read_events('202007_cat_quakeml.zip')
	>>> pairs = pair_picks_arrivals(cat[0],1)

	"""
	paired = []
	for arrival in ev.origins[origin_index].arrivals:
		tid = arrival.pick_id
		for pick in ev.picks:
			if pick.resource_id == tid:
				tpick = pick
				tpair = [tpick,arrival]
				paired.append(tpair)



	return paired


def get_phase_pairs(paired,phase):
	"""
	function get_phase_pairs
	selects phase pick-arrival pairs of a given phase
	[pick,arrival]

	example usage: 
	>>> pairs_Pn = get_phase_pairs(pairs,'Pn')

	"""
	phase_pairs = []
	for pair in paired:
		if pair[0].phase_hint == phase:
			phase_pairs.append(pair)
	return phase_pairs

def get_station_pairs(paired,network,station):
	station_pairs = []
	for pair in paired:
		if pair[0].waveform_id.station_code==station and pair[0].waveform_id.network_code==network:
			station_pairs.append(pair)
	return station_pairs



def writephasecsv(cat):
	"""
	writes a csv containing the info regarding just the important phases

	"""
	df = pd.DataFrame(columns = ['network','station','channel','P','Pg','Pn','S','Sg','Sn'])

        # add phases PKP and others like PP
	phases = ['P','Pg','Pn','S','Sg','Sn','PKP','PP','SKS']
	for event in cat:
		try:

			#find the origin that contains the arrivals
			origin_indexes = []
			for origin in event.origins:
				origin_indexes.append(len(origin.arrivals))
			origin_index = int(np.argmax(np.asarray(origin_indexes)))
			oi = origin_index
			event_type = event.event_type
			
			magnitude='NaN'
			try:
				for tmagnitude in event.magnitudes[:1]:
					magnitude=tmagnitude.mag	
			except Exception as e: print('No magnitude')

			pairs = pair_picks_arrivals(event,origin_index)

			# create a set of network.station codes, this info is in the Pick
			stations = set([pick.waveform_id.network_code+'.'+pick.waveform_id.station_code for pick in event.picks])
			#print('stations',len(stations),'picks',len(event.picks),'arrivals',len(event.origins[oi].arrivals))
			network_codes = [station.split('.')[0] for station in stations]
			station_codes = [station.split('.')[1] for station in stations]
			#print(tdf)

			tdf = pd.DataFrame()

			for network,station in zip(network_codes,station_codes):
				# get all the pick-arrival pairs for the given station
				sta_pairs = get_station_pairs(pairs,network,station)
				ptime='NaN';pgtime='NaN';pntime='NaN';stime='NaN';sgtime='NaN';sntime='NaN'
				pweight='NaN';pgweight='NaN';pnweight='NaN';sweight='NaN';sgweight='NaN';snweight='NaN';
				# add evaluation mode
				pev  = 'NaN'; sev  = 'NaN' 
				pgev = 'NaN'; sgev = 'NaN'
				pnev = 'NaN'; snev = 'NaN'
				pnev
				distance='NaN';azimuth='NaN';takeoff_angle='NaN'
				channel = (sta_pairs[-1][0].waveform_id.channel_code)[:2]
				

				for pair in sta_pairs:
					if pair[0].phase_hint == 'P':
						ptime = pair[0].time
						pweight = pair[1].time_weight
						pev = pair[0].evaluation_mode
					elif pair[0].phase_hint == 'Pg':
						pgtime = pair[0].time
						pgweight = pair[1].time_weight
						pgev = pair[0].evaluation_mode
					elif pair[0].phase_hint == 'Pn':
						pntime = pair[0].time
						pnweight = pair[1].time_weight
						pnev = pair[0].evaluation_mode
					elif pair[0].phase_hint =='S':
						stime = pair[0].time
						sweight = pair[1].time_weight
						sev = pair[0].evaluation_mode			
					elif pair[0].phase_hint =='Sg':
						sgtime = pair[0].time
						sgweight = pair[1].time_weight
						sgev = pair[0].evaluation_mode
					elif pair[0].phase_hint == 'Sn':
						sntime = pair[0].time
						snweight = pair[1].time_weight
						snev = pair[0].evaluation_mode
				# create a temporary dictionary for each station

				tdic = {'network':[network],'station':[station],'channel':channel,
					'P':[ptime],'Pg':[pgtime],'Pn':[pntime],'S':[stime],'Sg':[sgtime],'Sn':[sntime],
					'P_weight':[pweight],'Pg_weight':[pgweight],'Pn_weight':[pnweight],
					'S_weight':[sweight],'Sg_weight':[sgweight],'Sn_weight':[snweight],
					'P_evaluation_mode':[pev],
					'Pg_evaluation_mode':[pgev],
					'Pn_evaluation_mode':[pnev],
					'S_evaluation_mode':[sev],
					'Sg_evaluation_mode':[sgev],
					'Sn_evaluation_mode':[snev],
					'origin_time':[event.origins[oi].time],		
					'origin_time_uncertainty':[event.origins[oi].time_errors.uncertainty],
					'origin_latitude':[event.origins[oi].latitude],
					'origin_latitude_uncertainty':[event.origins[oi].latitude_errors.uncertainty],
					'origin_longitude':[event.origins[oi].longitude],
					'origin_longitude_uncertainty':[event.origins[oi].longitude_errors.uncertainty],
					'depth':[event.origins[oi].depth],
					'depth_uncertainty':[event.origins[oi].depth_errors.uncertainty],
					'origin_ID':[str(event.origins[oi].resource_id).split('/')[-1]],
					'distance':[pair[1].distance],
					'azimuth':[pair[1].azimuth],
					'takeoff_angle':[pair[1].takeoff_angle],
					'magnitude':[magnitude],'event_type':[event_type]}

				#print(tdic)
				ttdf = pd.DataFrame.from_dict(tdic)
				tdf = tdf.append(ttdf,ignore_index=True)
				
				# remove the lines that have no information 
				tdf = tdf[(tdf['P']!='NaN')|(tdf['Pg']!='NaN')|(tdf['Pn']!='NaN')|(tdf['S']!='NaN')|(tdf['Sg']!='NaN')|(tdf['Sn']!='NaN')] 	


			df = df.append(tdf,ignore_index=True)	
		
		except Exception as e:
			print(e)	
	
	return df


#if __name__ == "__main__":
cat = read_events(filename)
print(cat)
tt = writephasecsv(cat)

#outname = filename.split('.')[0].split('/')[1]+'.csv'
outname = filename.split('.')[0]+'.csv'
tt.to_csv(outname)
print(' Writing ',outname)
print(tt)
