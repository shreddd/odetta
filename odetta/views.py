from django.http import HttpResponse, Http404
from odetta.models import Fluxvals, MetaDd2D, Models, SearchForm, get_mu_max, get_time_max
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
from django.core.files import File
from odetta.settings import FITS_ROOT
import zipfile
import glob,os
import StringIO

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
            if search_form.cleaned_data['model_id']:
                return redirect(plot, search_form.cleaned_data["model_id"])

            # Searches for metadata matching the criteria
            search_query = {}
            for field in request.GET:
                if request.GET.get(field) and field != "page":
                    search_query[field] = request.GET.get(field)

            # Deals with paging of search results
            page = request.GET.get("page", 1)
            matched_models = Models.objects.filter(**search_query).order_by("m_type_id")
            result_list = MetaDd2D.objects.none()
            for model in matched_models:
                result_list = result_list | MetaDd2D.objects.filter(m_type_id=model.m_type_id).order_by("model_id").distinct("model_id")
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


def plot(request, model_id):
    meta_data = MetaDd2D.objects.filter(model_id=model_id).order_by("t_expl", "-mu")
    if meta_data.count() <= 0:
        raise Http404
    meta_data = meta_data[0]

    # Creates a detail array for display on table below graph
    # Excludes the fields in the excludes array
    details = []
    exclude = ["t_expl", "mu"]
    for field in meta_data._meta.get_all_field_names():
        if field not in exclude:
            details.append((meta_data._meta.get_field(field).verbose_name, getattr(meta_data, field.__str__())))
    return render_to_response("spectrum_detail.html", {"details": details, "meta_data": meta_data, "mu_max": get_mu_max(model_id), "time_max": get_time_max(model_id)}, context_instance=RequestContext(request))


def get_plot_data(request, model_id, time_step=0, mu_step=0):
    model = MetaDd2D.objects.filter(model_id=model_id)
    if model.count() <= 0:
        raise Http404

    try:
        all_time_steps = model.values("t_expl").distinct("t_expl").order_by("t_expl")
        t_expl = all_time_steps[int(time_step)]["t_expl"]
    except IndexError:
        return HttpResponse(simplejson.dumps({"success": False, "error": "time_step index out of bounds", "max_time_steps": all_time_steps.count()}), content_type="application/json")
    try:
        all_mu_steps = model.filter(t_expl=t_expl).values("mu").order_by("-mu")
        mu = all_mu_steps[int(mu_step)]["mu"]
    except IndexError:
        return HttpResponse(simplejson.dumps({"success": False, "error": "mu_step index out of bounds", "max_mu_steps": all_mu_steps.count()}), content_type="application/json")

    # Gets the meta data based on the calculated mu and t_expl
    # Uses range to prevent floating point errors
    meta_data = model.get(mu__range=(mu-0.01, mu+0.01), t_expl__range=(t_expl-0.01, t_expl+0.01))

    # Populates a flux data array from the spec_id of the selected meta_data
    qset = Fluxvals.objects.filter(spec_id=meta_data.spec_id)
    flux_data = []
    for rec in qset:
        flux_data.append({
            "wavelength": rec.wavelength,  # Graph's X-Axis
            "lum": rec.luminosity,  # Graph's Y-Axis
        })
    data = {
        "model_id": int(meta_data.model_id),
        "time_step": int(time_step),
        "t_expl": float(t_expl),
        "max_time_steps": all_time_steps.count()-1,
        "mu_step": int(mu_step),
        "mu": float(mu),
        "max_mu_steps": all_mu_steps.count()-1,
        "flux_data": flux_data,
    }
    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def batch_time_data(request, model_id, mu_step):
    model = MetaDd2D.objects.filter(model_id=model_id)

    if model.count() <= 0:
        raise Http404

    try:
        all_mu_steps = model.values("mu").distinct("mu").order_by("-mu")
        mu = all_mu_steps[int(mu_step)]["mu"]
    except IndexError:
        return HttpResponse(simplejson.dumps({"success": False, "error": "mu_step index out of bounds", "max_mu_steps": all_mu_steps.count()}), content_type="application/json")

    meta_datas = model.filter(mu__range=(mu-0.01, mu+0.01)).order_by("t_expl")
    data = []
    index = 0
    for m in meta_datas:
        data.append({
            "time_step": int(index),
            "mu_step": int(mu_step),
            "flux_data": [],
        })
        qset = Fluxvals.objects.filter(spec_id=m.spec_id)
        for rec in qset:
            data[index]['flux_data'].append({
                "wavelength": rec.wavelength,  # Graph's X-Axis
                "lum": rec.luminosity,  # Graph's Y-Axis
            })
        index += 1
    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def batch_angle_data(request, model_id, time_step):
    model = MetaDd2D.objects.filter(model_id=model_id)

    if model.count() <= 0:
        raise Http404

    try:
        all_time_steps = model.values("t_expl").distinct("t_expl").order_by("t_expl")
        t_expl = all_time_steps[int(time_step)]["t_expl"]
    except IndexError:
        return HttpResponse(simplejson.dumps({"success": False, "error": "time_step index out of bounds", "max_time_steps": all_time_steps.count()}), content_type="application/json")

    meta_datas = model.filter(t_expl=t_expl).order_by("-mu")
    data = []
    index = 0
    for m in meta_datas:
        data.append({
            "time_step": int(time_step),
            "mu_step": int(index),
            "flux_data": [],
        })
        qset = Fluxvals.objects.filter(spec_id=m.spec_id)
        for rec in qset:
            data[index]['flux_data'].append({
                "wavelength": rec.wavelength,  # Graph's X-Axis
                "lum": rec.luminosity,  # Graph's Y-Axis
            })
        index += 1
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


def plot_img(request, model_id, time_step=0, mu_step=0):
    model = MetaDd2D.objects.filter(model_id=model_id)
    if model.count() <= 0:
        raise Http404

    try:
        all_time_steps = model.values("t_expl").distinct("t_expl").order_by("t_expl")
        t_expl = all_time_steps[int(time_step)]["t_expl"]
        all_mu_steps = model.filter(t_expl=t_expl).values("mu").order_by("-mu")
        mu = all_mu_steps[int(mu_step)]["mu"]
    except IndexError:
        raise Http404

    # Gets the meta data based on the calculated mu and t_expl
    # Uses range to prevent floating point errors
    meta_data = model.get(mu__range=(mu-0.01, mu+0.01), t_expl__range=(t_expl-0.01, t_expl+0.01))

    # Populates a flux data array from the spec_id of the selected meta_data
    qset = Fluxvals.objects.filter(spec_id=meta_data.spec_id)
    wave = [rec.wavelength for rec in qset]
    lum = [rec.luminosity for rec in qset]
    ttle = 'Model '+str(spec_id)
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

def get_zip_file(request):
    string_file = StringIO.StringIO()
    zipped_file = zipfile.ZipFile(string_file, 'w', compression=zipfile.ZIP_DEFLATED)
    current_dir = os.getcwd()
    os.chdir(FITS_ROOT)
    for content in glob.glob("./*"):
        zipped_file.write(content)
    os.chdir(current_dir)
    zipped_file.close()
    contents = string_file.getvalue()
    # slash = FITS_ROOT.rfind("/")
    # fileName = FITS_ROOT[slash+1:]
    response = HttpResponse(contents, content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=blarg.zip'
    return response
    # zipped_file = zipfile.ZipFile(FITS_ROOT,'w')
    # for(file in )
    
