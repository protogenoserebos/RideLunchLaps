from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import BikeConfig
from .forms import BikeConfigForm

@login_required
def list_configs(request):
    configs = BikeConfig.objects.filter(owner=request.user).select_related("bike")
    return render(request, "bikeconfigs/list.html", {"configs": configs})

@login_required
def create_config(request):
    if request.method == "POST":
        form = BikeConfigForm(request.POST)
        if form.is_valid():
            cfg = form.save(commit=False)
            cfg.owner = request.user
            # (optionally) enforce that cfg.bike.owner == request.user
            if cfg.bike.owner_id != request.user.id:
                form.add_error("bike", "You can only add settings for your own bike.")
            else:
                cfg.save()
                return redirect("bikeconfigs:list")
    else:
        form = BikeConfigForm()
        form.fields["bike"].queryset = request.user.bikes.all()
    return render(request, "bikeconfigs/edit.html", {"form": form})

@login_required
def edit_config(request, pk):
    cfg = get_object_or_404(BikeConfig, pk=pk, owner=request.user)
    if request.method == "POST":
        form = BikeConfigForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save()
            return redirect("bikeconfigs:list")
    else:
        form = BikeConfigForm(instance=cfg)
        form.fields["bike"].queryset = request.user.bikes.all()
    return render(request, "bikeconfigs/edit.html", {"form": form, "cfg": cfg})
