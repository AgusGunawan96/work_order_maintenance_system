from django.shortcuts import render

# Create your views here.



def starter_kit(request):
    context={"breadcrumb":{"parent":"Color Version","child":"Layout Light"}}
    return render(request,'starter_kit/index.html',context)

