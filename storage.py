import matplotlib.pyplot as plt
import numpy as np
import math

def tierpoints(limits,costs):
	# Calculate plot points for tiered storage costs
	# - limits is a list of data storage limits
	# - costs is a list of equivalent prices, 
	#      where costs[n] is the price paid for storage >= limits[n]
	if len(limits) != len(costs):
		raise ValueError

	xvals = [0]; yvals = [0]

	for n in range(len(limits)):
		if n != 0:
			xvals.append(limits[n-1]+0.00001)	
			yvals.append(costs[n])	
		xvals.append(limits[n])
		yvals.append(costs[n])

	return xvals, yvals

def s3cost(size, pergb):
	# Estimated cost for S3 EU storage for duplicity backups

	if size == 0: 
		return 0
	
	size = math.ceil(size)
			
	transfercost = (size/12-1)*0.15

	filesize = 25 # MB
	nputs = (size*1000/12)/filesize 		# per month
	putcost = math.ceil(nputs/1000)*0.01
	getcost = putcost

	storagecost = size * pergb

	monthcost = transfercost + putcost + getcost + storagecost
	return monthcost * 12
	

D = np.arange(0., 200., 0.01)
# S3
xvals = [x/100.0 for x in range(200*100+1)]
s3full = [s3cost(x, 0.15) for x in xvals]
s3red = [s3cost(x, 0.1) for x in xvals]
plt.plot(xvals, s3full, label="S3 Europe")
plt.plot(xvals, s3red, label="S3 Europe - reduced redundancy")

def bitfolkcost(size, per5gb):
	return math.ceil(size/5)*per5gb

gbp2usd = 1.6018
# bfmon = [bitfolkcost(x,0.4*gbp2usd*12) for x in xvals]
# bfyr = [bitfolkcost(x,4*gbp2usd) for x in xvals]
# #plt.plot(xvals, bfmon, label="BitFolk (pay monthly)")
# plt.plot(xvals, bfyr, label="BitFolk (pay yearly)")

# dropbox
dblimits = [2, 50, 100]
dbcosts = [0, 9.99 * 12, 19.99 * 12]
x, y = tierpoints(dblimits,dbcosts)
plt.plot(x, y, label="Dropbox")

# Google
# glimits = [1, 20, 80, 200]
# gcosts = [0, 5, 20, 50]
# x,y = tierpoints(glimits, gcosts)
# plt.plot(x, y, label="Google Docs")

# Ubuntu One
u1packs = np.ceil((D-2)/20)
u1mon = u1packs * 2.99 * 12
u1yr = u1packs * 29.99
plt.plot(D,u1mon, label="Ubuntu One (Pay Monthly)")
plt.plot(D,u1yr, label="Ubuntu One (Pay Yearly)")

# rsync.net
def rsynccost(size, pergb = 0.8):
    """Given a dataset size in GB, return a the monthly cost 
    of storing that data at rsync.net, based on their tiered 
    discounts."""
    rsyncgb = pergb * 12
    rslimits = [0, 50, 99, 199, 399]
    rscosts = [0, rsyncgb, rsyncgb*0.9, rsyncgb*0.8, rsyncgb*0.7]
    
    rssize = math.ceil(size)

    if rssize == 0: return 0

    for n in range(len(rslimits)-1,-1,-1):
        if size <= rslimits[n] and rssize > rslimits[n-1]:
            return rssize * rscosts[n]

    raise ValueError # out of range

#rsynccosts = [x*rsyncgb for x in xvals]
rsyncstdcosts = [rsynccost(x) for x in xvals]
rsyncglocosts = [rsynccost(x, 1.4) for x in xvals]
plt.plot(xvals, rsyncstdcosts, label="rsync.net - Standard")
plt.plot(xvals, rsyncglocosts, label="rsync.net - Georedundant")

plt.ylabel('Yearly cost (USD)')
plt.xlabel('Data stored (GB)')
plt.legend(loc=2, prop={'size': 'small' })
plt.axis(ymin=0)
plt.axvline(110)
plt.show()
