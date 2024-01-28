
############################################################
# This code checks all the csv files derived from the      #
# quakeml files and creates a list of all the networks     #
# encountered. It checks all the data centers avaliable    #
# through obspy to see from which data center each network #
# is available.                                            #
# the result is written to allnets.txt                     #
# ##########################################################

import pandas as pd
import glob


from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import URL_MAPPINGS

from obspy.core import UTCDateTime as UT

# get a set of all the station codes
allnets = []
filenames = glob.glob('/Users/albert/Pn/quakeml/201*csv')
for filename in filenames:
	df = pd.read_csv(filename)
	nets = df['network'].to_numpy()
	nets = list(set(nets))
	#print(nets)
	for net in nets:
		allnets.append(net)
allnets = list(set(list(allnets)))
print(allnets)
print(len(allnets))
fout = open('network_codes.txt','w+')
for net in allnets[1:]:
	fout.write(str(net))
	fout.write('\n')
fout.close()


reftime= UT('20150101')
alldics = []
for key in list(sorted(URL_MAPPINGS.keys())):
	print(key)
	client = Client(key)
	tdic = []
	
	tdic.append(key)
	for network in allnets[1:]:
		print(key,network)
		try:
			st = client.get_waveforms(network=network,station='*',location='*',channel='BH?,HH?,HN?',
						starttime=reftime,endtime=reftime+30)
			tdic.append(network)
		except Exception as e:
			print(e)
			print(client,network)

	alldics.append(tdic)

fout = open('allnets.txt','w+')
for dic in alldics:
	fout.write('---------------')
	fout.write('\n')
	for element in dic:
		fout.write(str(element))
		fout.write('\n')
fout.close()

	
	

