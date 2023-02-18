from django.shortcuts import render

# Create your views here.
def index(request):
    context={"breadcrumb":{"parent":"Color Version","child":"Layout Light"}}
    return render(request,'master_app/index.html',context)

def login(request):

    return render(request, 'master_app/login.html')