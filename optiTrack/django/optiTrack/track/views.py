from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms.formsets import formset_factory
from django.conf import settings

from track.models import Tblemployee
from track.models import Tbldept
from forms import *

import os
import re

def index(request):
	context = {}
	return render(request, 'trackIndex.html', context)

def departments(request):
	listObjs = Tbldept.objects.all()
	context = {'listObjs': listObjs}
	return render(request, 'tblDept.html', context)

def employee(request):
	listObjs = Tblemployee.objects.all()
	context = {'listObjs': listObjs}	
	return render(request, 'tblEmployees.html', context)

def addEmployee(request):
	addTuple = ()
	errors = []
	if request.method == 'POST':
		if not request.POST.get('firstname'):
			errors.append('Please Enter First Name.')
		if not request.POST.get('lastname'):
			errors.append('Please Enter Last Name.')

		if not errors:
			firstname = request.POST.get('firstname')
			lastname = request.POST.get('lastname')
			department = request.POST.get('department')
			addTuple = (firstname, lastname, department)
			e = Tblemployee(firstname=firstname, lastname=lastname, department=department)
			e.save()

	deptList = Tbldept.objects.all()
	context = {'errors': errors, 'added': addTuple, 'deptList': deptList}
	return render(request, 'addEmployee.html', context)

def travelerSetupForm(request):
	error = None
	if request.method == 'POST':
		if not request.POST.get('num_rows'):
			error = 'Please enter a valid number for number of rows!'

		if not error:
			num_rows = request.POST.get('num_rows')
			return HttpResponseRedirect('/track/travelerform/'+num_rows+'/')

	context = {'error': error, 'setupForm': TravelerSetupForm()}
	return render(request, 'travelerFormSetup.html', context)

def travelerForm(request, numForms=10):
	error = None
	title = ['OpNum', 'DeptID', 'Description', 'CycleDays']
	rTitle = ['OpNum', 'MachRes', 'MachHrs']
	lTitle = ['OpNum', 'LaborRes', 'LaborHrs']
	columns = ['op_num', 'work_center', 'routing_steps', 'engineering_cycle_time_estimate']
	rCol = ['op_num', 'machine_resource_requirements', 'machine_resource_utilization_time']
	lCol = ['op_num', 'labor_resource_requirements', 'labor_resource_utilization_time']
	outFile = settings.MEDIA_URL + "tform.csv"
	resOutFile = settings.MEDIA_URL + "rform.csv"
	labOutFile = settings.MEDIA_URL + "lform.csv"
	numForms = int(numForms)
	TravelerFormSet = formset_factory(TravelerForm, extra=numForms)

	if request.method == 'POST':
		formset = TravelerFormSet(request.POST, request.FILES)
		print request.POST.get('form-0-machine_resource_requirements')

		if formset.is_valid():	
			# only proceed if the forms are valid...
			f = open(outFile, 'w')
			for t in title:
				f.write(t+',')
			f.write('\n')

			fRes = open(resOutFile, 'w')
			for t in rTitle:
				fRes.write(t+',')
			fRes.write('\n')

			fLab = open(labOutFile, 'w')
			for t in lTitle:
				fLab.write(t+',')
			fLab.write('\n')


			# writing data rows:
			for formInd in range(numForms):
				for col in columns:
					if request.POST.get('form-'+str(formInd)+'-'+col):
						f.write(request.POST.get('form-'+str(formInd)+'-'+col) + ',')
					else:
						f.write(' ,')
				f.write('\n')

				op_num = request.POST.get('form-'+str(formInd)+'-op_num')
				machRes = request.POST.get('form-'+str(formInd)+'-machine_resource_requirements')
				machTime = request.POST.get('form-'+str(formInd)+'-machine_resource_utilization_time')
				# clean up carriage return...
				machRes = re.sub('\r', '', machRes)
				machTime = re.sub('\r','', machTime)
				if machRes or machTime:
					machRes = machRes.split('\n')
					machTime = machTime.split('\n')
					for i in range(max(len(machRes), len(machTime))):
						fRes.write(op_num+',')
						if i < len(machRes):
							fRes.write(machRes[i])
						fRes.write(' ,')
						if i < len(machTime):
							fRes.write(machTime[i])
						fRes.write(' ,')
						fRes.write('\n')

				op_num = request.POST.get('form-'+str(formInd)+'-op_num')
				laborRes = request.POST.get('form-'+str(formInd)+'-labor_resource_requirements')
				laborTime = request.POST.get('form-'+str(formInd)+'-labor_resource_utilization_time')
				# clean up carriage return
				laborRes = re.sub('\r', '', laborRes)
				laborTime = re.sub('\r', '', laborTime)
				if laborRes or laborTime:
					laborRes = laborRes.split('\n')
					laborTime = laborTime.split('\n')
					for i in range(max(len(laborRes), len(laborTime))):
						fLab.write(op_num+',')
						if i < len(laborRes):
							fLab.write(laborRes[i])
						fLab.write(' ,')
						if i < len(laborTime):
							fLab.write(laborTime[i])
						fLab.write(' ,')
						fLab.write('\n')


			f.close()
			fRes.close()
			fLab.close()

		else:
			error = formset.errors +'Please fill all rows with valid information.\n'

	formset = TravelerFormSet()
	return render(request, 'travelerForm.html', {'form': TravelerForm(), 'formset': formset, 'error': error})

def tformcsv(request):
	return HttpResponse('media/form.txt')