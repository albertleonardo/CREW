

###################################################
# Takes the csv files containing the picks, the   #
# allnets.txt file containing datacenter-network  #
# information and downloads the waveform data     #
###################################################

import sys
import glob
import pandas as pd
import numpy as np

from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime as UT

index = int(sys.argv[1])
# make it work on a single one file

# load the database info
fin = open('allnets.txt','r')
lines = fin.readlines()
#print(lines)
# arrange in directories
indices = []
for i,line in enumerate(lines):
	if line == '---------------\n':
		indices.append(i)
indices.append(len(lines))

print(indices)
alldics = []	
for i in range(0,len(indices)-1):
	tdic = lines[indices[i]+1:indices[i+1]]
	tdic = [element.split('\n')[0] for element in tdic]
	#print(tdic)
	if len(tdic) > 1:
		alldics.append(tdic)
print(alldics)


#some parameters
total_length = 360.
pre_length   = 60.
pos_length   = total_length - pre_length


#bring a dataframe and start the download

filenames = sorted(glob.glob('/Users/albert/Pn/quakeml/2013*csv'))
for filename in filenames[index:index+1]:
	print('-----------------------------------------------')
	print(filename)

	df = pd.read_csv(filename)
	# replace a little problem
	df = df.replace(['1970-01-01T00:00:00.000000Z'],'0')
	df = df.fillna('NaN')
	#df = df[(df['Pg']!='NaN')&(df['Sg']!='NaN')]
	print(df)	


	Pndf = df[df['Pn'] != 'NaN']
	Pgdf = df[df['Pg'] != 'NaN']
	#Pdf  = df[df['P']  != 'NaN']
	#print(Pndf)
	#print(Pgdf)

	for tdic in alldics:
		clientkey = tdic[0]
		client = Client(clientkey)
		for network in tdic[1:]:
			print(network)
			tempnetdf = Pndf[Pndf['network'] == network]
			print(tempnetdf)
			for j,row in tempnetdf.iterrows():
				try:
					st = client.get_waveforms(network=network,station=row['station'],location='*',channel='*',
						starttime=UT(row['Pn'])-pre_length,endtime=UT(row['Pn'])+pos_length)
					st.merge()
					for tr in st: 
						if tr.stats.sampling_rate < 20: 
							st.remove(tr)
					if len(st)>0:
						outname = row['network']+'.'+row['station']+'.'+row['Pn']+'.Pn.mseed'
						st.write('mseedfiles/'+outname,format='MSEED')
						print(st)
						print('saved as ',outname)
				except Exception as e:
					print(e)
		
				
			tempnetdf = Pgdf[Pgdf['network'] == network]
			print(tempnetdf)
			for j,row in tempnetdf.iterrows():
				try:
					st = client.get_waveforms(network=network,station=row['station'],location='*',channel='*',
						starttime=UT(row['Pg'])-pre_length,endtime=UT(row['Pg'])+pos_length)
					st.merge()
					for tr in st: 
						if tr.stats.sampling_rate < 20: 
							st.remove(tr)
					if len(st)>0:
						outname = row['network']+'.'+row['station']+'.'+row['Pg']+'.Pg.mseed'
						st.write('mseedfiles/'+outname,format='MSEED')
						print(st)
						print('saved as ',outname)
				except Exception as e:
					print(e)
			"""		
			tempnetdf = Pdf[Pdf['network'] == network]
			print(tempnetdf)
			for j,row in tempnetdf.iterrows():
				try:
					st = client.get_waveforms(network=network,station=row['station'],location='*',channel=row['channel']+'*',
						starttime=UT(row['P'])-pre_length,endtime=UT(row['P'])+pos_length)
					st.merge()
					#for tr in st: 
					#	if tr.stats.sampling_rate != 100: 
					#		st.remove(tr)
					if len(st)>0:
						outname = row['network']+'.'+row['station']+'.'+row['P']+'.P.mseed'
						st.write('mseedfiles/'+outname,format='MSEED')
						print(st)
						print('saved as ',outname)
				except Exception as e:
					print(e)

			"""
