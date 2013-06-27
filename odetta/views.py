from django.http import HttpResponse
from odetta.models import Fluxvals, MetaDd2D, Models, SearchForm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import pylab as pl
from django.shortcuts import render_to_response, redirect
import simplejson
from django.forms.models import model_to_dict
from odetta_utils import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from simple_chi2 import *


def home_page(request):
    return render_to_response('base.html', context_instance=RequestContext(request))


def search_models(request):
    search_form = SearchForm()
    results = []
    MAX_ENTRIES = 10
    if request.method == "GET" and len(request.GET):
        search_form = SearchForm(data=request.GET)
        if search_form.is_valid():

            # Shows the detailed page if m_id is inputed
            if search_form.cleaned_data['m_id']:
                return redirect(plot, search_form.cleaned_data["m_id"])

            # Searches for metadata matching the criteria
            search_query = Q()
            if search_form.cleaned_data["percent_oxygen"]:
                search_query = search_query | Q(percent_oxygen=search_form.cleaned_data["percent_oxygen"])
            if search_form.cleaned_data["percent_carbon"]:
                search_query = search_query | Q(percent_carbon=search_form.cleaned_data["percent_carbon"])

            # Deals with paging of search results
            page = request.GET.get("page", 1)
            result_list = MetaDd2D.objects.filter(search_query).order_by("m_id")
            pages = Paginator(result_list, MAX_ENTRIES)
            try:
                results = pages.page(page)
            except PageNotAnInteger:
                results = pages.page(1)
            except EmptyPage:
                results = pages.page(pages.num_pages)

            # Creates a range of pages (like on the bottom of google search)
            page_range = []
            if results.number <= MAX_ENTRIES/2:
                page_range = pages.page_range[:MAX_ENTRIES]
            elif results.number >= pages.page_range[-1]-MAX_ENTRIES/2:
                page_range = pages.page_range[-MAX_ENTRIES:]
            else:
                page_range = range(results.number-4, results.number+5)

            # Creates a querystring without the page number
            temp = request.GET.copy()
            if temp.get("page"):
                temp.pop("page")
            query_string = temp.urlencode()

            return render_to_response('search.html', {"form": search_form, "results": results, "page_range": page_range, "q_string": query_string}, context_instance=RequestContext(request))
    return render_to_response('search.html', {"form": search_form}, context_instance=RequestContext(request))


def plot(request, id):
    qset = Fluxvals.objects.filter(m_id=id)
    meta_data = MetaDd2D.objects.get(m_id=id)
    flux_data = []
    for rec in qset:
        flux_data.append({
            "wavelength": rec.wavelength,
            "lum": rec.luminosity,
        })
    data = {
        "meta": model_to_dict(meta_data),
        "flux_data": flux_data
    }
    details = []
    for field in meta_data._meta.get_all_field_names():
        details.append((meta_data._meta.get_field(field).verbose_name, getattr(meta_data, field.__str__())))
    # raise Exception(details)
    return render_to_response("spectrum_detail.html", {"data": simplejson.dumps(data), "details": details, "meta_data": meta_data}, context_instance=RequestContext(request))


def ajax_plot(request, id):
    qset = Fluxvals.objects.filter(m_id=id)
    meta_data = MetaDD2D.objects.get(m_id=id)
    flux_data = []
    for rec in qset:
        flux_data.append({
            "wavelength": rec.wavelength,
            "lum": rec.luminosity,
        })
    data = {
        "meta": model_to_dict(meta_data),
        "flux_data": flux_data
    }
    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def fitter(request):
    return render_to_response("fitter_form.html", context_instance=RequestContext(request))


def about(request):
    return render_to_response("about.html", context_instance=RequestContext(request))


def run_all_data(request, x2, y2, y2var):
    #get id's
    qset = Fluxvals.objects.distinct('m_id')
    m_id = [rec.m_id for rec in qset]
    print "There are " + len(m_id) + " spectra in DB. Running them all..."

    #get wavelengths
    qset2 = Fluxvals.objects.filter(m_id=1)
    waves = [rec.wavelength for rec in qset2]
    ##need to add something to make sure we have same grid for both spectra
    ##HERE

    output = []
    for id in m_id:
        wave = [rec.wavelength for rec in qset]
        lum = [rec.luminosity for rec in qset]
        [chi2, dof, a] = compute_chi2(waves, lum, y2, y2var)
        output.append([m_id, chi2, dof, a])

    response = HttpResponse(content_type='???')
    return response


def plot_mid(request, id):
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
    if int(request.GET.get("download", 0)) == 1:
        response['Content-Disposition'] = 'attachment; filename="graph.png"'
    canvas.print_png(response)
    return response


def plot_few(request,id):
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
    ax.plot(wave, lum)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response



def text(request):
    return HttpResponse('Sample Text')
