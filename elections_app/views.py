from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.views.generic import ListView, DetailView
from elections_app.models import Person, Info, Election
from elections_app.worker import load_from_url, load_from_json
import threading
import logging


logger = logging.getLogger('elections')

class LoadDataForm(forms.Form):
    file_field = forms.FileField(required=False)
    url = forms.CharField(required=False)
    html_text = forms.CharField(widget=forms.Textarea, required=False)
    filter_string = forms.CharField(required=False)

@login_required(login_url='/admin')
def load_data(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LoadDataForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            url = form.cleaned_data['url']
            html_text = form.cleaned_data['html_text']
            filter_string = form.cleaned_data['filter_string']
            if url or html_text:
              t = threading.Thread(target=load_from_url,
                                   args=(url, html_text, filter_string))
              t.setDaemon(False)
              t.start()
            else:
              load_from_json(form.cleaned_data['file_field'])
            return HttpResponseRedirect('/admin/') # Redirect after POST
    else:
        logger.info("Открыли страницу загрузки данных")
        form = LoadDataForm() # An unbound form

    return render(request, 'loaddata.html', {
        'form': form,
    })


class ElectionList(ListView):
    paginate_by = 30
    def get_queryset(self):
        queryset = Election.objects.all()
        if 'election_name' in self.request.GET:
            election_name = self.request.GET['election_name']
            queryset = queryset.filter(name__icontains=election_name)
            self.paginate_by = 0

        return queryset


class ElectionDetail(DetailView):
    model = Election


class PersonDetail(DetailView):
    model = Person


class InfoList(ListView):
    paginate_by = 100
    def get_queryset(self):
        queryset = Info.objects.all()
        if 'person_name' in self.request.GET:
            person_name = self.request.GET['person_name']
            if person_name:
                queryset = queryset.filter(person__name__icontains=person_name)
                self.paginate_by = 0
        if 'election_name' in self.request.GET:
            election_name = self.request.GET['election_name']
            if election_name:
                queryset = queryset.filter(election__name__icontains=election_name)
                self.paginate_by = 0
        if 'firm_name' in self.request.GET:
            firm_name = self.request.GET['firm_name']
            if firm_name:
                queryset = queryset.filter(firm__icontains=firm_name)
                self.paginate_by = 0

        return queryset
