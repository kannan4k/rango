from django.template import RequestContext
from django.shortcuts import render_to_response


def index(request):
	context = RequestContext(request)
	context_dict = {'boldmessage':"This is bold message from Context"}
	return render_to_response('rango/index.html',context_dict, context)

def about(request):
	context = RequestContext(request)
	context_dict = {'boldmessage':"kannan.jpg"}
	return render_to_response('rango/about.html',context_dict, context)
