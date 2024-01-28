
# widget to check for the quality of examples, save the name and the evaluation gf the example

# Plot filtered and unfiltered waveforms

import skynet
import sys
import matplotlib.pyplot as plt


fname = sys.argv[1]

start_index = 0
if sys.argv[2]:
	start_index = int(sys.argv[2])


data = skynet.open(fname)

n_data = len(data)
names = list(data.keys())

evaluations = []
results_name = fname+'_human_screening'
outfile = open(results_name,'a')


for i in range(start_index,n_data):
	print(i)
	t_name = names[i]
	example = data[names[i]] 
	#fig = plt.figure()
	#plt.subplot(2,1,1)
	#plot = skynet.plot_example_long(example,filtered=False)
	#plt.subplot(2,1,2)
	plot = skynet.plot_example_both(example,(16,7))
	#plot.show()
	#plt.show(block=False)
	plt.show()
	#plt.pause(1)
	#plt.ion()
	evaluation = input('Good -g- of Bad -b-?')
	evaluations.append((t_name,evaluation ))
	eval_line = t_name+' '+evaluation
	outfile.write(eval_line)
	outfile.write('\n')

	if evaluation=='close':
		break

	plt.close()


#with open('evaluations','wb') as file:
#	pickle.dump(evaluations,file)

