from django.views.generic.edit import FormView
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt   
from django.http import HttpResponse
from django.template import loader, Context
from django.template.loader import render_to_string

import os

from compare import *

@csrf_exempt
def home(request):
	if request.method=="POST":
		try:
			file1 = request.FILES['file1']
			
			fileHandle1 = open("./attachments/" + file1.name, 'wb+')
			for chunk in file1.chunks():
				fileHandle1.write(chunk)
			fileHandle1.close()
			
			file2 = request.FILES['file2']
			fileHandle2 = open("./attachments/" + file2.name, 'wb+')
			for chunk in file2.chunks():
				fileHandle2.write(chunk)
			fileHandle2.close()
		except KeyError, MultiValueDictKeyError:
			return HttpResponse("Invalid Filename", status=400);
		return HttpResponse(status=204)
	else:
		return render_to_response('form.html')
	
def compare(request):
	if request.method !="GET":
		return HttpResponse("Invalid operation", status=404)
	
	#check for handle invalid inputs and process them
	outputMap = {}
	outputMap["errorStr"] = ""
	templateObj = None
	utility = None
	
	try:
		file1 = request.GET.get('file1')
		file2 = request.GET.get('file2')
		if len(file1) <= 0 and len(file2) <= 0:
			raise Exception("Chose a file to compare");
		filedsToIgnore = request.GET.get('filedsToIgnore').split(",")
		file1Path = os.path.abspath('./attachments/' + file1)
		file2Path = os.path.abspath('./attachments/' + file2)
		utility = CompareUtility();
		outputMap = utility.compare(file1Path, file2Path, filedsToIgnore)
		templateObj = loader.get_template('results.html')
	except Exception, e:
		templateObj = loader.get_template('error.html')
		outputMap["errorStr"] = str(e)
		
	return HttpResponse(templateObj.render(outputMap))
