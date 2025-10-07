from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.text import capfirst
from django.contrib.auth.decorators import login_required
from ll_buildbike.models import (
    LLBike, BikeLike, LLBikeImg, LLComponentSus, LLComponentWheel, LLComponentDrive,
    LLComponentCockpit, LLComponentBrakes, LLComponentSeat,
)
from ll_buildbike.constants import (
    SUS_FRONTSUS_FIELDS, SUS_REARSUS_FIELDS,
    WHEEL_FRONT_TIRE_FIELDS, WHEEL_REAR_TIRE_FIELDS, WHEEL_COMPLETE_FIELDS, WHEEL_HUB_FIELDS, WHEEL_RIMS_FIELDS,
    DRIVE_DERAILLEUR_FIELDS, DRIVE_CASSETTE_FIELDS, DRIVE_CHAINRING_FIELDS, DRIVE_CHAIN_FIELDS, DRIVE_BB_FIELDS,
    DRIVE_CRANKS_FIELDS, DRIVE_PEDAL_FIELDS,
    COCKPIT_GRIPS_FIELDS, COCKPIT_BARS_FIELDS, COCKPIT_LEVER_FIELDS, COCKPIT_SHIFTER_FIELDS, COCKPIT_STEM_FIELDS, COCKPIT_HEADSET_FIELDS,
    BRAKES_BRAKE_FIELDS, BRAKES_ROTOR_FIELDS, BRAKES_LEVER_FIELDS, BRAKES_PADS_FIELDS,
    SEAT_SEATPOST_FIELDS, SEAT_SADDLE_FIELDS,
)

@login_required
def bikedash(request):
    bikes = (
        LLBike.objects
        .filter(owner=request.user)              # only mine
        .order_by(models.F("is_default").desc(), "-date_created")
        .prefetch_related(
            "bike_images",
            "suspension_components",
            "wheel_components",
            "drivetrain_components",
            "cockpit_components",
            "brake_components",
            "seat_components",
        )
    )
    liked_ids = set(BikeLike.objects.filter(user=request.user, bike__in=bikes).values_list("bike_id", flat=True))

BIKE_SPEC_FIELDS = [
    "bike_make", "bike_model", "bike_year",
    "bike_type", "bike_size", "bike_discipline", "bike_build",
]

SECTION_CONFIG = [
    ("Suspension", "suspension_components", SUS_FRONTSUS_FIELDS + SUS_REARSUS_FIELDS),
    ("Wheels", "wheel_components", WHEEL_COMPLETE_FIELDS + WHEEL_HUB_FIELDS + WHEEL_RIMS_FIELDS + WHEEL_FRONT_TIRE_FIELDS + WHEEL_REAR_TIRE_FIELDS),
    ("Drivetrain", "drivetrain_components", DRIVE_DERAILLEUR_FIELDS + DRIVE_CASSETTE_FIELDS + DRIVE_CHAIN_FIELDS + DRIVE_CHAINRING_FIELDS + DRIVE_BB_FIELDS + DRIVE_CRANKS_FIELDS + DRIVE_PEDAL_FIELDS),
    ("Cockpit", "cockpit_components", COCKPIT_GRIPS_FIELDS + COCKPIT_BARS_FIELDS + COCKPIT_LEVER_FIELDS + COCKPIT_SHIFTER_FIELDS + COCKPIT_STEM_FIELDS + COCKPIT_HEADSET_FIELDS),
    ("Brakes", "brake_components", BRAKES_BRAKE_FIELDS + BRAKES_ROTOR_FIELDS + BRAKES_LEVER_FIELDS + BRAKES_PADS_FIELDS),
    ("Seat", "seat_components", SEAT_SEATPOST_FIELDS + SEAT_SADDLE_FIELDS),
]

def _rows_for(instance, field_names):
    rows = []
    for name in field_names:
        try:
            field_obj = instance._meta.get_field(name)
        except Exception:
            continue
        val = getattr(instance, name, None)
        if val in (None, "", [], (), {}):
            continue
        if isinstance(field_obj, (models.FileField, models.ImageField)):
            url = getattr(val, "url", None)
            if not url:
                continue
            display = url
            is_url = True
        else:
            display = str(val)
            is_url = False
        rows.append({"label": capfirst(field_obj.verbose_name), "value": display, "is_url": is_url})
    return rows


def bikedash(request):
    bikes = (
        LLBike.objects
        .order_by(models.F("is_default").desc(), "-date_created")
        .prefetch_related(
            "bike_images",
            "suspension_components",
            "wheel_components",
            "drivetrain_components",
            "cockpit_components",
            "brake_components",
            "seat_components",
        )
    )

    cards = []
    for b in bikes:
        cover_url = b.bike_img.url if b.bike_img else None
        gallery_urls = [img.bike_img.url for img in b.bike_images.all() if img.bike_img]

        specs = _rows_for(b, BIKE_SPEC_FIELDS)

        sections = []
        for title, relname, fields in SECTION_CONFIG:
            instance_cards = []
            for inst in getattr(b, relname).all():
                rows = _rows_for(inst, fields)
                if rows:
                    instance_cards.append(rows)
            if instance_cards:
                sections.append({"title": title, "instances": instance_cards})

        cards.append({"bike": b, "cover": cover_url, "gallery": gallery_urls, "specs": specs, "sections": sections})

    return render(request, "bikedash/bikedashboard.html", {"cards": cards})

@require_POST
def set_default_bike(request, pk):
    bike = get_object_or_404(LLBike, pk=pk)
    LLBike.objects.update(is_default=False)
    bike.is_default = True
    bike.save()
    return redirect("bikedash:bikedash")

@require_POST
def delete_bike(request, pk):
    bike = get_object_or_404(LLBike, pk=pk)
    bike.delete()  # on_delete=CASCADE will remove components/images
    return redirect("bikedash:bikedash")
