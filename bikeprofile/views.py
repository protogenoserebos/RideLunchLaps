from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from ll_buildbike.models import (
    LLBike, LLComponentSus, LLComponentDrive, LLComponentWheel,
    LLComponentCockpit, LLComponentBrakes, LLComponentSeat,
)

# (Re-use your field lists if you have ll_buildbike.constants; inline here for brevity)
BIKE_SPEC_FIELDS = [
    "bike_make", "bike_model", "bike_year", "bike_type", "bike_size", "bike_discipline", "bike_build",
]

SECTION_CONFIG = [
    ("Suspension", "suspension_components", [
        "bike_frontsus_make", "bike_frontsus_model", "bike_frontsus_travel", "bike_frontsus_year",
        "bike_frontsus_review", "bike_frontsus_addtnotes",
        "bike_rearsus_make", "bike_rearsus_model", "bike_rearsus_eyetoeye", "bike_rearsus_travel",
        "bike_rearsus_year", "bike_rearsus_review", "bike_rearsus_addtnotes",
    ]),
    ("Wheels", "wheel_components", [
        "bike_complete_wheel_make", "bike_complete_wheel_model","bike_complete_wheel_size","bike_complete_wheel_type",
        "bike_complete_wheel_review","bike_complete_wheel_addtnotes",
        "bike_hubs_make","bike_hubs_model","bike_hubs_eng","bike_hubs_frontwidth","bike_hubs_rearwidth","bike_hubs_axle",
        "bike_hubs_review","bike_hubs_addtnotes",
        "bike_rims_make","bike_rims_model","bike_rims_holecount","bike_rims_material","bike_rims_size",
        "bike_rims_review","bike_rims_addtnotes",
        "bike_fronttire_make","bike_fronttire_model","bike_fronttire_width","bike_fronttire_quality",
        "bike_fronttire_review","bike_fronttire_addtnotes",
        "bike_reartire_make","bike_reartire_model","bike_reartire_width","bike_reartire_quality",
        "bike_reartire_review","bike_reartire_addtnotes",
    ]),
    ("Drivetrain", "drivetrain_components", [
        "bike_derailleur_type","bike_derailleur_make","bike_derailleur_model","bike_derailleur_year",
        "bike_derailleur_review","bike_derailleur_addtnotes",
        "bike_cassette_make","bike_cassette_model","bike_cassette_year","bike_cassette_range","bike_cassette_speed",
        "bike_cassette_review","bike_cassette_addtnotes",
        "bike_chain_make","bike_chain_model","bike_chain_speed","bike_chain_review","bike_chain_addtnotes",
        "bike_chainring_make","bike_chainring_model","bike_chainring_bcd","bike_chainring_teeth",
        "bike_chainring_review","bike_chainring_addtnotes",
        "bike_bottombracket_make","bike_bottombracket_model","bike_bottombracket_fitment","bike_bottombracket_width",
        "bike_bottombracket_review","bike_bottombracket_addtnotes",
        "bike_cranks_make","bike_cranks_model","bike_cranks_length","bike_cranks_material",
        "bike_cranks_review","bike_cranks_addtnotes",
        "bike_pedals_type","bike_pedals_make","bike_pedals_model","bike_pedals_review","bike_pedals_addtnotes",
    ]),
    ("Cockpit", "cockpit_components", [
        "bike_headset_make","bike_headset_model","bike_headset_type","bike_headset_top","bike_headset_bottom",
        "bike_headset_review","bike_headset_addtnotes",
        "bike_stem_make","bike_stem_model","bike_stem_length","bike_stem_stack","bike_stem_opening",
        "bike_stem_review","bike_stem_addtnotes",
        "bike_dropperlever_make","bike_dropperlever_model","bike_dropperlever_review","bike_dropperlever_addtnotes",
        "bike_brakelevers_make","bike_brakelevers_model","bike_brakelevers_review","bike_brakelevers_addtnotes",
        "bike_shifter_make","bike_shifter_model","bike_shifter_speed","bike_shifter_review","bike_shifter_addtnotes",
        "bike_grips_make","bike_grips_model","bike_grips_review","bike_grips_addtnotes",
        "bike_bars_make","bike_bars_model","bike_bars_material","bike_bars_width","bike_bars_rise","bike_bars_diam",
        "bike_bars_review","bike_bars_addtnotes",
    ]),
    ("Brakes", "brake_components", [
        "bike_brakes_make","bike_brakes_model","bike_brakes_pistons","bike_brakes_review","bike_brakes_addtnotes",
        "bike_brakerotor_make","bike_brakerotor_model","bike_brakerotor_size","bike_brakerotor_attach",
        "bike_brakerotor_review","bike_brakerotor_addtnotes",
        "bike_brakelevers_make","bike_brakelevers_model","bike_brakelevers_review","bike_brakelevers_addtnotes",
        "bike_brakepads_makemodel","bike_brakepads_material","bike_brakepads_review","bike_brakepads_addtnotes",
    ]),
    ("Seat", "seat_components", [
        "bike_seatpost_type","bike_seatpost_make","bike_seatpost_model","bike_seatpost_travel","bike_seatpost_width",
        "bike_seatpost_review","bike_seatpost_addtnotes",
        "bike_saddle_make","bike_saddle_model","bike_saddle_review","bike_saddle_addtnotes",
    ]),
]



User = get_user_model()

def bike_detail_by_slug(request, username, slug):
    owner = get_object_or_404(User, username=username)
    bike = get_object_or_404(LLBike, owner=owner, slug=slug)
    return render(request, "bikeprofile/detail.html", {"bike": bike})

def bike_detail_public(request, public_id):
    bike = get_object_or_404(LLBike, public_id=public_id)
    return render(request, "bikeprofile/detail.html", {"bike": bike})

def _rows_for(instance, field_names):
    rows = []
    for name in field_names:
        try:
            field = instance._meta.get_field(name)
        except Exception:
            continue
        val = getattr(instance, name, None)
        if val in (None, "", [], (), {}):
            continue
        if isinstance(field, (models.FileField, models.ImageField)):
            url = getattr(val, "url", None)
            if not url:
                continue
            display = url
            is_url = True
        else:
            display = str(val)
            is_url = False
        rows.append({"label": field.verbose_name.title(), "value": display, "is_url": is_url})
    return rows

def bike_detail(request, public_id):
    bike = get_object_or_404(
        LLBike.objects.select_related("owner")
        .prefetch_related(
            "bike_images",
            "suspension_components",
            "wheel_components",
            "drivetrain_components",
            "cockpit_components",
            "brake_components",
            "seat_components",
        ),
        public_id=public_id
    )

    cover_url = bike.bike_img.url if bike.bike_img else None
    gallery = [img.bike_img.url for img in bike.bike_images.all() if img.bike_img]

    specs = _rows_for(bike, BIKE_SPEC_FIELDS)

    sections = []
    for title, relname, fields in SECTION_CONFIG:
        instance_cards = []
        for inst in getattr(bike, relname).all():
            rows = _rows_for(inst, fields)
            if rows:
                instance_cards.append(rows)
        if instance_cards:
            sections.append({"title": title, "instances": instance_cards})

    return render(request, "bikeprofile/detail.html", {
        "bike": bike,
        "cover": cover_url,
        "gallery": gallery,
        "specs": specs,
        "sections": sections,
    })

from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from ll_buildbike.models import LLBike

User = get_user_model()

def bike_detail_by_slug(request, username, slug):
    owner = get_object_or_404(User, username=username)
    bike = get_object_or_404(LLBike, owner=owner, slug=slug)
    return render(request, "bikeprofile/detail.html", {"bike": bike})

def bike_detail_public(request, public_id):
    bike = get_object_or_404(LLBike, public_id=public_id)
    return render(request, "bikeprofile/detail.html", {"bike": bike})