from __future__ import unicode_literals
from django.db import models
from django import forms

class Publication(models.Model):
    modeltype = models.CharField(max_length=40, blank = True)
    modeldim = models.IntegerField()
    date_entered = models.DateField()
    citation = models.CharField(max_length=200, blank=True)
    sntype = models.CharField(max_length=10, blank = True)
    pub_id = models.IntegerField()

    class Meta:
        db_table = 'publication'

class Chi2Test(models.Model):
    fname = models.CharField(max_length=200, blank=True)
    chi2dof = models.FloatField(null=True, blank=True)
    chi2dof_bin = models.FloatField(null=True, blank=True)
    dof = models.IntegerField(null=True, blank=True)
    dofb = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'chi2test'

class Spectra(models.Model):
    model_id = models.IntegerField()
    spec_id = models.IntegerField(primary_key=True)
    t_expl= models.FloatField(null=True,blank=True)
    mu = models.FloatField(null=True,blank=True)
    phi = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'spectra'

class Fluxvals(models.Model):
    spec_id = models.IntegerField(primary_key=True)
    wavelength = models.FloatField()
    luminosity = models.FloatField(null=True, blank=True)
    photon_count = models.FloatField(null=True, blank=True)
    t_expl = models.FloatField(null=True, blank=True)
    phi = models.FloatField(null=True, blank=True)
    mu = models.FloatField(null=True, blank=True)
    model_id = models.IntegerField()

    class Meta:
        db_table = 'fluxvals'


class MetaDd2D(models.Model):
    spec_id = models.BigIntegerField(primary_key=True)
    model_id = models.IntegerField()
    m_type_id = models.IntegerField()
    modelname = models.CharField(max_length=40, blank=True)
    modeltype = models.CharField(max_length=40, blank=True)
    modeldim = models.SmallIntegerField(null=True, blank=True)
    mass_wd = models.FloatField(null=True, blank=True)
    percent_carbon = models.FloatField(null=True, blank=True)
    percent_oxygen = models.FloatField(null=True, blank=True)
    n_ignit = models.IntegerField(null=True, blank=True)
    r_min_ignit = models.FloatField(null=True, blank=True)
    cos_alpha = models.FloatField(null=True, blank=True)
    stdev = models.FloatField(null=True, blank=True)
    ka_min = models.FloatField(null=True, blank=True)
    rho_min = models.FloatField(null=True, blank=True)
    rho_max = models.FloatField(null=True, blank=True)
    comments = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'meta_dd2d'

    @property
    def date_entered(self):
        return Models.objects.values("date_entered").get(m_type_id=self.m_type_id)['date_entered']

    @property
    def sntype(self):
        return Models.objects.values("sntype").get(m_type_id=self.m_type_id)['sntype']

    @property
    def citation(self):
        return Models.objects.values("citation").get(m_type_id=self.m_type_id)['citation']


def get_time_max(model_id):
    return Spectra.objects.filter(model_id=model_id).values("t_expl").distinct("t_expl").order_by("t_expl").count() - 1

def get_mu_max(model_id):
    return Spectra.objects.filter(model_id=model_id).values("mu").distinct("mu").order_by("-mu").count() - 1


class Models(models.Model):
    modeltype = models.CharField(max_length=40, blank=True)
    modeldim = models.SmallIntegerField(null=True, blank=True)
    date_entered = models.DateField(null=True, blank=True)
    citation = models.CharField(max_length=200, blank=True)
    sntype = models.CharField(max_length=10, blank=True)
    m_type_id = models.SmallIntegerField(null=True, blank=True, primary_key=True)

    class Meta:
        db_table = 'models'


class SearchForm(forms.Form):
    model_id = forms.IntegerField(required=False, label='Model ID')
    modeltype = forms.CharField(required=False, label="Model Type")
    modeldim = forms.IntegerField(required=False, label="Model Dimension")
    date_entered = forms.DateField(required=False, label="Date Entered")
    citation = forms.CharField(required=False, label="Citation")
    sntype = forms.CharField(required=False, label="SN Type")
