from django.shortcuts import render
from django.http import Http404, HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('jadi ini merupakan Index dari Timing App')
    return render(request, 'timing_app/index.html')