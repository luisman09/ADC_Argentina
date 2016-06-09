from __future__ import unicode_literals

from django.db import models

class Arg_Centro(models.Model):
    cue = models.IntegerField(primary_key=True)
    escuela = models.CharField(max_length=128)
    dir_escuela = models.CharField(max_length=128, blank=True, null=True)
    provincia = models.CharField(max_length=64)
    distrito = models.CharField(max_length=64)
    barrio = models.CharField(max_length=64)

    def __unicode__(self):
        return str(self.cue) + " " + self.escuela

    class Meta:
        managed = False
        db_table = 'arg_centro'
        ordering = ['cue']
