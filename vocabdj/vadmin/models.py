from django.db import models
from django.contrib.auth.models import User

class Title(models.Model):
    '''A title a person can have, for example: mr, ms, miss, mrs, dr'''
    title = models.CharField(max_length=20, primary_key=True)
    notes = models.CharField(max_length=50, blank=True)
    
    def __unicode__(self):
        return self.title

class Location(models.Model):
    '''A user can work in a particular location or organisation.'''
    location = models.CharField(max_length=20, primary_key=True)
    notes = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return self.location


class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    title = models.ForeignKey(Title)
    location = models.ForeignKey(Location)
    notes = models.TextField(blank=True)
  
    def __unicode__(self):
        return '%s %s'%(self.title, self.user)

#Automatically create profile if a view tries to look at profile.
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])