# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Fluxvals(models.Model):
    m_id = models.BigIntegerField(primary_key=True)
    wavelength = models.FloatField()
    luminosity = models.FloatField(null=True, blank=True)
    photon_count = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'fluxvals'

class MetaDD2D(models.Model):
    m_id = models.BigIntegerField(primary_key=True)
    modelname = models.CharField(max_length=40, blank=True)
    modeltype = models.CharField(max_length=40, blank=True)
    modeldim = models.SmallIntegerField(null=True, blank=True)
    t_expl = models.FloatField(null=True, blank=True)
    phi = models.FloatField(null=True, blank=True)
    mu = models.FloatField(null=True, blank=True)
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
        db_table = u'meta_dd2d'

class Models(models.Model):
    modeltype = models.CharField(max_length=40, blank=True)
    modeldim = models.SmallIntegerField(null=True, blank=True)
    date_entered = models.DateField(null=True, blank=True)
    citation = models.CharField(max_length=200, blank=True)
    sntype = models.CharField(max_length=10, blank=True)
    class Meta:
        db_table = u'models'

class Chi2Test(models.Model):
    fname = models.CharField(max_length=200, blank=True)
    chi2dof = models.FloatField(null=True, blank=True)
    chi2dof_bin = models.FloatField(null=True, blank=True)
    dof = models.IntegerField(null=True, blank=True)
    dofb = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'chi2test'

