from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from elections_app.views import ElectionList, ElectionDetail

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'elections.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', ElectionList.as_view(), name='home'),
    url(r'^election/(?P<pk>[0-9]+)/$', ElectionDetail.as_view(), name='election'),
    url(r'^load_data/', 'elections_app.views.load_data', name='load_data'),

)
