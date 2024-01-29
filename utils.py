
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

plt.rcParams['font.family']='Helvetica'
plt.rcParams['font.size']=18


def plot_example(example,filtered=False):
    traces=example[()]
    if filtered:
        traces  = bandpass_data(traces)
        traces = traces / np.max(np.abs(traces))

    fig = plt.figure(figsize=(16,4),tight_layout=True)
    gs  = gridspec.GridSpec(1,4)



    ax = fig.add_subplot(gs[0,0:3])
    for i in range(len(traces)):
        #x = np.arange(0,300,0.01)
        plt.plot(traces[i]-i*2,linewidth=0.5,c='k')
        plt.text(28000,-i*2+0.3,example.attrs['channels'][i],bbox=dict(boxstyle="round",fc='white'))#+channels[i])
        #plt.hlines(-3,0,30000)
        #plt.hlines(-1,0,30000)
    


        if example.attrs['P_arrival_sample'] != 'NaN':
            pg_pos = example.attrs['P_arrival_sample']
            plt.scatter(pg_pos,-2*i,s=4000,c='r',marker='|',label='P',linewidth=1)
            if i==0:plt.text(pg_pos-600,-5.2,'P',c='r')
        if example.attrs['Pg_arrival_sample'] != 'NaN':
            pg_pos = example.attrs['Pg_arrival_sample']
            plt.scatter(pg_pos,-2*i,s=4000,c='r',marker='|',label='Pg',linewidth=1)
            if i==0:plt.text(pg_pos,1.2,'Pg',c='r')
        if example.attrs['Pn_arrival_sample'] != 'NaN':
            pn_pos = example.attrs['Pn_arrival_sample']
            plt.scatter(pn_pos,-2*i,s=4000,c='r',marker='|',label='Pn')
            if i==0:plt.text(pn_pos-1000,1.2,'Pn',c='r')


        if example.attrs['S_arrival_sample'] != 'NaN':
            sg_pos = example.attrs['S_arrival_sample']
            plt.scatter(sg_pos,-2*i,s=4000,c='b',marker='|',label='S')
            if i==0:plt.text(sg_pos,-5.2,'S',c='b')
        if example.attrs['Sg_arrival_sample'] != 'NaN':
            sg_pos = example.attrs['Sg_arrival_sample']
            plt.scatter(sg_pos,-2*i,s=4000,c='b',marker='|',label='Sg')
            if i==0:plt.text(sg_pos,1.2,'Sg',c='b')
        if example.attrs['Sn_arrival_sample'] != 'NaN':
            sn_pos = example.attrs['Sn_arrival_sample']
            plt.scatter(sn_pos,-2*i,s=4000,c='b',marker='|',label='Sn')
            if i==0:plt.text(sn_pos-1000,1.2,'Sn',c='b')

    plt.ylim(-6,2)
    plt.yticks([])
    plt.xlim(0,30000)
    plt.xticks(np.arange(0,30001,6000),np.arange(0,301,60))
    plt.xlabel('seconds')
    plt.title(example.name)
    ax = fig.add_subplot(gs[0,3])
    ax.axis('off')

    id_ = example.attrs['station_network_code']+'.'+example.attrs['station_code']+'..'+example.attrs['channels'][0][:2]+'*'

    plt.text(0,1,id_)
    plt.text(0,0,example.attrs['source_origin_time'])
    plt.text(0,-1,'Origin Longitude = '+str(np.round(example.attrs['source_longitude_deg'],2)))
    plt.text(0,-2,'Origin Latitude    = '+str(np.round(example.attrs['source_latitude_deg'],2)))
    plt.text(0,-3,'Origin Depth       = '+str(np.round(example.attrs['source_depth_km'],2)))
    plt.text(0,-4,'Magnitude          = '+str(np.round(example.attrs['source_magnitude'],1)))
    plt.text(0,-5,'Distance             = '+str(np.round(example.attrs['path_ep_distance_deg'],2)) )

    if filtered:
        plt.text(0,-5.9,'Bandpassed',fontsize=12,color='red')

    plt.yticks([]);plt.xticks([])
    plt.ylim(-6,2)



    return fig
