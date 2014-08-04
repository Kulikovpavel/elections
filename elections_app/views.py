from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import django_tables2 as tables
from django.views.generic import ListView, DetailView
from elections_app.models import Person, Info, Election
import json
import codecs

from datetime import datetime

class LoadDataForm(forms.Form):
    file_field = forms.FileField()

def load_data(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = LoadDataForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            load_from_json(form.cleaned_data['file_field'])
            return HttpResponseRedirect('/admin/') # Redirect after POST
    else:
        form = LoadDataForm() # An unbound form

    return render(request, 'loaddata.html', {
        'form': form,
    })

def load_from_json(json_file):
  data = json.loads(json_file.read().decode('utf-8'))
  for d in data:
    name = d[0]
    date = datetime.strptime(d[1], '%d.%m.%Y')
    url = d[2]
    try:
      election = Election.objects.get(name=name, date=date)
      if election.url != url:
        election.url = url
        election.save()
    except Election.DoesNotExist:
      election = Election(name=name, date=date, url=url)
      election.save()


    candidates = d[3]
    for c in candidates:
      try:
        person = Person.objects.get(name=c[0], birthdate=datetime.strptime(c[2], '%d.%m.%Y'))
      except Person.DoesNotExist:
        person = Person(name=c[0], birthdate=datetime.strptime(c[2], '%d.%m.%Y'))
        person.save()

      try:
        info = Info.objects.get(person=person, election=election)
      except Info.DoesNotExist:
        info = Info(person=person, election=election)
        info.save()
      print(person)
      info.url = c[1]
      info.party = c[3]
      info.address = c[4]
      info.edu = c[5]
      info.firm = c[6]
      info.job = c[7]
      info.dep = c[8]
      info.criminal = c[9]
      info.status = c[10]
      info.district = c[11]
      info.save()

class ElectionList(ListView):
    model = Election

class ElectionDetail(DetailView):
    model = Election
    def get_context_data(self, **kwargs):
      context = super(ElectionDetail, self).get_context_data(**kwargs)
      table = InfoTable(self.object.info_set.all())
      table.order_by = "person"
      tables.RequestConfig(self.request, paginate=False).configure(table)
      context['table'] = table
      return context

class InfoTable(tables.Table):
    class Meta:
        model = Info
        # add class="paleblue" to <table> tag
        attrs = {"id": "paleblue"}
        exclude = ("id", "election" )

def home(request):
    return HttpResponse("Hello, world. You're at the poll index.")
