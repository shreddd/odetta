import numpy as np
import math

def demean(y1,y2,y2var):
	#assumes numpy arrays
	mean1 = np.mean(y1)
	y1 = y1/mean1 -1 
	#y1 = [yy/mean1 - 1 for yy in y1]
	mean2 = np.mean(y2)
	y2 = y2/mean2 -1 
	#y2 = [yy/mean2 - 1 for yy in y2]
	y2var = y2var/mean2 -1 
	#y2var = [yy/mean2 for yy in y2var]
	return [y1,y2,y2var,mean1,mean2]



def bin_spec(wave,flux,fluxerr,u,q,npb=5,name='test',save_this=False):
	#calculate nbin
	nbin = int(math.floor(len(wave)/npb))
	#print 'nbin=',nbin

	bin_wave = []
	bin_flux = []
	bin_fluxerr = []
	bin_u = []
	bin_q = []
	if save_this:
		savefile = open(name+'.binspec','w')
	for i in range(nbin):
	     if i==nbin-1:
	             bin_flux.append( np.mean(flux[npb*nbin:]))
	             bin_wave.append( np.mean(wave[npb*nbin:]))
	             bin_fluxerr.append( np.mean(fluxerr[npb*nbin:]))
	             bin_u.append( np.mean(u[npb*nbin:]))
	             bin_q.append( np.mean(q[npb*nbin:]))
		     if save_this:
			print >> savefile, bin_wave[i],bin_flux[i],bin_fluxerr[i],bin_u[i],bin_q[i]
	     else:
	             bin_flux.append(np.mean(flux[npb*i:npb*(i+1)]))
	             bin_fluxerr.append(np.mean(fluxerr[npb*i:npb*(i+1)]))
	             bin_u.append(np.mean(u[npb*i:npb*(i+1)]))
	             bin_q.append(np.mean(q[npb*i:npb*(i+1)]))
	             bin_wave.append(np.mean(wave[npb*i:npb*(i+1)]))
		     if save_this:
			print >> savefile, bin_wave[i],bin_flux[i],bin_fluxerr[i],bin_u[i],bin_q[i]
	if save_this: 
		savefile.close()
	return [bin_wave,bin_flux,bin_fluxerr,bin_u,bin_q]

def psql_all_data():
	import pg
	conn=pg.connect("odetta","scidb1.nersc.gov",5432,None,None,"odetta_admin","spectronic20")
	data=conn.query("SELECT m_id,wavelength,luminosity,photon_count from fluxvals")
	ids=conn.query("SELECT distinct m_id from fluxvals")
	return [data, ids]	 


def read_mspec(fname):
	[wave,lum,q,u,ph_ct] = np.loadtxt(fname,dtype="float",unpack=True) # double check the order of these polarization paramters
	return [wave,lum,q,u,ph_ct]

def read_data(fname):
	try:
		[wave,flux,fluxerr] = np.loadtxt(fname,dtype="float",unpack=True)
		return [wave,flux,fluxerr] 
	except ValueError:
		[wave,flux] = np.loadtxt(fname,dtype="float",unpack=True) 
		return [wave,flux]


def interpol(x1,y1,x_out,plot=False):
	from scipy.signal import cspline1d, cspline1d_eval
	#assumes that data points are evenly spaced

	dx=x1[1]-x1[0]
	cj=cspline1d(y1)
	y_out=cspline1d_eval(cj,x_out,dx=dx,x0=x1[0])
	if plot:
		from pylab import plot, show,legend
		plot(x_out,y_out,'ob',x1,y1,'xg',ms=2)
		legend(['interpolated','original'])
		show()

	return y_out


