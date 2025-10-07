from django.shortcuts import render


# Create your views here.

def bikesearch(request):
    """The bike search page for Lunch Laps"""
    return render(request, 'll_bikesearch/bikesearch.html')