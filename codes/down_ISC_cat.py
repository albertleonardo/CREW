import sys
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime as UT

year = int(sys.argv[1]) ;month = int(sys.argv[2]); day = int(sys.argv[3])
start = UT(year=year,month=month,day=day)
end   = UT(year=year,month=month,day=day+1)
client = Client('ISC')
minmag=1
cat = client.get_events(starttime=start,endtime=end,includearrivals=True,minmagnitude=minmag)
out = 'ISC_cat_'+str(year)+'_'+str(month).rjust(2,'0')+'_'+str(day).rjust(2,'0')
print(cat)
cat.write(out,format='QUAKEML')

# This catalog has every network as IR, got to check later which network stations belong to
