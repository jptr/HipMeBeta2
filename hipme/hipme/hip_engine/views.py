from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

def test(request):
    return render_to_response('test.html', context_instance=RequestContext(request))