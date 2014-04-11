from django.conf.urls import patterns, url
from django.conf import settings

from track import views

urlpatterns = patterns('',
	url(r'^travelerform/$', views.travelerSetupForm, name='travelerSetupForm'),
	url(r'^travelerform/(?P<numForms>\d{1,2})/$', views.travelerForm, name='travelerForm'),
	url(r'^addemployee/$', views.addEmployee, name='addEmployee'),
	url(r'^employee/$', views.employee, name='employee'),
	url(r'^departments/$', views.departments, name='departments'),
	url(r'^$', views.index, name='index'),
)