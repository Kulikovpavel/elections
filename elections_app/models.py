from django.db import models

# Create your models here.
class Person(models.Model):
  name = models.CharField(max_length=200)
  birthdate = models.DateField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name + " " + str(self.birthdate)

  class Meta:
    ordering = ('name', 'birthdate', )

class Election(models.Model):
  name = models.CharField(max_length=300)
  date = models.DateField()
  url = models.CharField(max_length=500)
  candidates = models.ManyToManyField(Person, through='Info')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name + " " + str(self.date)

  class Meta:
    ordering = ('date', 'name', )

class Info(models.Model):
  person = models.ForeignKey(Person)
  election = models.ForeignKey(Election)

  district = models.CharField(max_length=200)
  party = models.CharField(max_length=300)
  address = models.CharField(max_length=1000)
  edu = models.CharField(max_length=200)
  firm = models.CharField(max_length=200)
  job = models.CharField(max_length=200)
  dep = models.CharField(max_length=200)  # previous deputat status
  criminal = models.CharField(max_length=1000)
  status = models.CharField(max_length=200)
  url = models.CharField(max_length=500)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  def __str__(self):
    return str(self.person) + " " + str(self.election)
    
