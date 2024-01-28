
# collects the data that passes the given conditions
# s after P
# arrivals within window


import sys
import h5py
import glob
import skynet
import numpy as np



import multiprocessing

# calling skynet is expensive

def count_arrivals(example_name):
	"""
	count how many nonzero arrivals are there
	"""
	example=data[example_name]
	count = 0
	if example.attrs['P_arrival_sample']!=0:
		count +=1
	if example.attrs['Pn_arrival_sample']!=0:
		count +=1
	if example.attrs['Pg_arrival_sample']!=0:
		count +=1
	if example.attrs['S_arrival_sample']!=0:
		count +=1
	if example.attrs['Sg_arrival_sample']!=0:
		count +=1
	if example.attrs['Sn_arrival_sample']!=0:
		count +=1

	return example.name,count


def check_example(example):

	if ((example.attrs['Pn_arrival_sample']!=0) & (example.attrs['Pg_arrival_sample']!=0) & (example.attrs['Sn_arrival_sample']!=0) &(example.attrs['Sg_arrival_sample']!=0)):
		return True	
	else:
		return False

def position_check(example):
        if example.attrs['P_arrival_sample']<0:
                return False
        if example.attrs['Pn_arrival_sample']<0:
                return False
        if example.attrs['Pg_arrival_sample']<0:
                return False
        if example.attrs['S_arrival_sample']>30000:
                return False
        if example.attrs['Sn_arrival_sample']>30000:
                return False
        if example.attrs['Sg_arrival_sample']>30000:
                return False
        if example.attrs['P_arrival_sample']>30000:
                return False
        if example.attrs['Pn_arrival_sample']>30000:
                return False
        if example.attrs['Pg_arrival_sample']>30000:
                return False
        else:
                return True


def length_check(example):
	X = example[()]
	if X[np.abs(X)<1e-10].shape[0] < 45000:
		return True


def check_sp_lag(example):
	p,s = skynet.get_first_arrivals(example)
	if s<=p:
		return False
	else:
		return True
# take the year

year  = sys.argv[1]

# filename of the 4_arrivals file
#fname1 =  year+'_screening_results_second_g'
#filename of the hdf5 file for the year
fname2 = year+'_chunk_isc_mseed_data.hdf5'
#fname2 =  'clean_uhq_'+year+'_isc_mseed_data.hdf5'

fname2=sys.argv[1]
year=fname2
# filename of the new file to write
hf = h5py.File(year+'_clean_safe.hdf5','w')
g1 = hf.create_group('data') 

# read in the 4_arrivals file
#fin = open(fname1,'r')
#lines = fin.readlines()


#open the data file
f = h5py.File(fname2,'r')
data = f['data']

names = list(data.keys())

for i,name in enumerate(names):
	try:
		#name = line.split()[0]
		print(i,name)
		example = data[name]
		print('check', check_example(example))
		print('position' , position_check(example))
		if (position_check(example)==True)&(length_check(example)==True)&(check_sp_lag(example)==True):
			print('success')
			data.copy(data[name],hf['/data'],name)
	except Exception as e:
		print(e,name)

"""
pool = multiprocessing.Pool()
inputs = names
outputs_async = pool.map_async(count_arrivals,inputs,chunksize=500)
outputs = outputs_async.get()
"""

hf.close()





