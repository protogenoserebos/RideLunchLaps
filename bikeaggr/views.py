from django.shortcuts import render
from bikeaggr.models import PBBike


# Create your views here.

def index(request):
    """The return homepage for Lunch Laps"""
    return render(request, 'll_buildbike/bikebuilder.html')

def bikesearchagg(request):
    """Bike search aggregator for PinkBike."""
    trailbikes = PBBike.objects.all()
    context = {'trailbikes': trailbikes}
    return render(request, 'bikeaggr/bikesearchaggr.html', context)