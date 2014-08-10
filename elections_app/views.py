from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import django_tables2 as tables
from django.views.generic import ListView, DetailView
from elections_app.models import Person, Info, Election
from elections_app.worker import load_from_url, load_from_json
import threading


class LoadDataForm(forms.Form):
    file_field = forms.FileField(required=False)
    url = forms.CharField(required=False)
    filter_string = forms.CharField(required=False)

def load_data(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LoadDataForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            url = form.cleaned_data['url']
            filter_string = form.cleaned_data['filter_string']
            if url:
              t = threading.Thread(target=load_from_url,
                                   args=(url, filter_string))
              t.setDaemon(True)
              t.start()                  
            else:
              load_from_json(form.cleaned_data['file_field'])
            return HttpResponseRedirect('/admin/') # Redirect after POST
    else:
        form = LoadDataForm() # An unbound form

    return render(request, 'loaddata.html', {
        'form': form,
    })


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
    url = tables.URLColumn("url", accessor='url')
    date = tables.Column(accessor='person.birthdate')
    class Meta:
        model = Info
        # add class="paleblue" to <table> tag
        attrs = {"id": "paleblue"}
        exclude = ("id", "election" )
        sequence = ("person", "date", "...")

def home(request):
    return HttpResponse("Hello, world. You're at the poll index.")
