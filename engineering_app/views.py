from django.shortcuts import render

# Create your views here.
def index(request):
    
    return render(request, 'engineering_app/index.html')