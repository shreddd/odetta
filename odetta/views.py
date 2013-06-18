from django.http import HttpResponse
#from odetta_utils import *
#from simple_chi2 import *

def home_page(request):
	from django.shortcuts import render_to_response
	return render_to_response('base.html')	


def run_all_data(request,x2,y2,y2var):
	from odetta.models import Fluxvals

	#get id's
	qset1 = Fluxvals.objects.distinct('m_id')
	m_id = [rec.m_id for rec in qset]
	print "There are "+len(m_id)+" spectra in DB. Running them all..."
	
	#get wavelengths
	qset2 = Fluxvals.objects.filter(m_id=1)
	waves = [rec.wavelength for rec in qset2]
	##need to add something to make sure we have same grid for both spectra
	##HERE	


	output = []
	for id in m_id:

		wave = [rec.wavelength for rec in qset]
		lum = [rec.luminosity for rec in qset]
		[chi2,dof,a] = compute_chi2(waves,lum,y2,y2var)
		output.append([m_id,chi2,dof,a])
	

	response = HttpResponse(content_type='???')
    	return response


def plot_mid(request,id):
	from odetta.models import Fluxvals
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	import pylab as pl

	qset = Fluxvals.objects.filter(m_id=id)
	wave = [rec.wavelength for rec in qset]
	lum = [rec.luminosity for rec in qset]
	ttle = 'Model '+str(id)
	xl = 'Wavelength (A)'
	yl = 'Luminosity'
	
	fig = Figure()
	ax = fig.add_subplot(111)
	ax.set_title(ttle)
	ax.set_xlabel(xl)
	ax.set_ylabel(yl)
	ax.plot(wave,lum)

	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
    	return response



def plot_few(request,id):
	from odetta.models import Fluxvals
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	import pylab as pl

	qset = Fluxvals.objects.filter(m_id=id)
	wave = [rec.wavelength for rec in qset]
	lum = [rec.luminosity for rec in qset]
	ttle = 'Model '+str(id)
	xl = 'Wavelength (A)'
	yl = 'Luminosity'
	
	fig = Figure()
	ax = fig.add_subplot(111)
	ax.set_title(ttle)
	ax.set_xlabel(xl)
	ax.set_ylabel(yl)
	ax.plot(wave,lum)

	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
    	return response




def text(request):
	return HttpResponse('Sample Text')
