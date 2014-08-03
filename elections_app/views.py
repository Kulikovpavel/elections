from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.views.generic import ListView, DetailView
from elections_app.models import Person, Info, Election
import json
from datetime import datetime

class LoadDataForm(forms.Form):
    json_text = forms.CharField(widget=forms.Textarea)

def load_data(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = LoadDataForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            load_from_json(form.cleaned_data['json_text'])
            return HttpResponseRedirect('/admin/') # Redirect after POST
    else:
        form = LoadDataForm() # An unbound form

    return render(request, 'loaddata.html', {
        'form': form,
    })

def load_from_json(json_text):
  data = json.loads(json_text)
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
      info.save()

class ElectionList(ListView):
    model = Election

class ElectionDetail(DetailView):
    model = Election


def home(request):
    return HttpResponse("Hello, world. You're at the poll index.")
