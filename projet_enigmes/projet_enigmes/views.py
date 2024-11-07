from django.shortcuts import render

def a_propos(request):
    return render(request, 'a_propos.html')