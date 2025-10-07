# views.py
import os
from django import forms
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.utils.text import capfirst
from formtools.wizard.views import SessionWizardView
from django.utils.decorators import method_decorator
from django.db.models import F

 
from .forms import (
    BikeForm,
    ComponentsFormWheel,
    ComponentsFormSus,
    ComponentsFormDrive,
    ComponentsFormCockpit,
    ComponentsFormBrakes,
    ComponentsFormSeat,
)
from .models import (
    LLBike,
    LLBikeImg,
    LLComponentSus,
    LLComponentDrive,
    LLComponentWheel,
    LLComponentBrakes,
    LLComponentCockpit,
    LLComponentSeat,
    BikeLike,
)

# ---------- Steps (images step removed) ----------
FORMS = [
    ("bike", BikeForm),
    ("suspension", ComponentsFormSus),
    ("drivetrain", ComponentsFormDrive),
    ("wheels", ComponentsFormWheel),
    ("brakes", ComponentsFormBrakes),
    ("cockpit", ComponentsFormCockpit),
    ("seat", ComponentsFormSeat),
    ("review", forms.Form),  # no fields
]

TEMPLATES = {
    "bike": "ll_buildbike/bike_wizard/bike_step.html",
    "suspension": "ll_buildbike/bike_wizard/suspension_step.html",
    "drivetrain": "ll_buildbike/bike_wizard/drivetrain_step.html",
    "wheels": "ll_buildbike/bike_wizard/wheels_step.html",
    "cockpit": "ll_buildbike/bike_wizard/cockpit_step.html",
    "brakes": "ll_buildbike/bike_wizard/brakes_step.html",
    "seat": "ll_buildbike/bike_wizard/seat_step.html",
    "review": "ll_buildbike/bike_wizard/review_step.html",
}

FRIENDLY_TITLES = {
    "bike": "Bike",
    "suspension": "Suspension",
    "wheels": "Wheels",
    "drivetrain": "Drivetrain",
    "cockpit": "Cockpit",
    "brakes": "Brakes",
    "seat": "Seat",
    "review": "Review",
}

def index(request):
    return render(request, "ll_buildbike/index.html")

def bikebuild(request):
    bikes = LLBike.objects.all()
    return render(request, "ll_buildbike/bikebuilder.html", {"bikes": bikes})

def bikesearch(request):
    return render(request, "ll_bikesearch/bikesearch.html")

@login_required
def toggle_like(request, pk):
    bike = get_object_or_404(LLBike, pk=pk)
    like, created = BikeLike.objects.get_or_create(user=request.user, bike=bike)
    if created:
        LLBike.objects.filter(pk=bike.pk).update(like_count=F("like_count") + 1)
    else:
        like.delete()
        LLBike.objects.filter(pk=bike.pk).update(like_count=F("like_count") - 1)
    # bounce back where we came from
    next_url = request.META.get("HTTP_REFERER") or "home"
    return redirect(next_url)


@method_decorator(login_required, name="dispatch")
class BikeCreateWizard(SessionWizardView):
    """Multi-step bike creation with early-submit support."""
    form_list = FORMS
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "temp"))

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # --- helper: did this form collect any real values? ---
    @staticmethod
    def _has_any_value(form):
        for name, field in form.fields.items():
            if name == "gallery":  # skip non-model field decision (we handle separately)
                continue
            val = form.cleaned_data.get(name, None)
            if val not in (None, "", [], (), {}, False):
                return True
        return False

    from django.utils.text import capfirst

    def get_context_data(self, form, **kwargs):
        ctx = super().get_context_data(form=form, **kwargs)

        # current step title
        ctx["current_title"] = FRIENDLY_TITLES.get(self.steps.current, capfirst(self.steps.current))

        # next button label already exists as next_title in your code
        nxt = self.steps.next
        ctx["next_title"] = FRIENDLY_TITLES.get(nxt, capfirst(nxt)) if nxt else None

        # a list of {name, title} for nav rendering
        step_order = list(self.get_form_list().keys())  # e.g. ["bike","suspension",...]
        ctx["step_titles"] = [
            {"name": s, "title": FRIENDLY_TITLES.get(s, capfirst(s))}
            for s in step_order
        ]

        # Build review data as a sequence so we can show titles without dict subscripting
        if self.steps.current == "review":
            def stringify(val):
                if isinstance(val, (list, tuple, set)):
                    return ", ".join(map(str, val))
                return "" if val is None else str(val)

            all_data_seq = []
            for step in step_order:
                if step == "review":
                    continue
                data = self.get_cleaned_data_for_step(step) or {}
                all_data_seq.append({
                    "name": step,
                    "title": FRIENDLY_TITLES.get(step, capfirst(step)),
                    "data": {k: stringify(v) for k, v in data.items()},
                })
            ctx["all_data_seq"] = all_data_seq

        return ctx
    
  
    def post(self, request, *args, **kwargs):
        # Early-finish path only
        if "finish_now" in request.POST:
            form = self.get_form(data=request.POST, files=request.FILES)
            if not form.is_valid():
                return self.render(form)

            # Persist current step like the base class does
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))

            # Build validated forms for visited steps (incl. current), stop at first unvisited
            completed = []
            for step in self.get_form_list().keys():
                step_data = self.storage.get_step_data(step)
                step_files = self.storage.get_step_files(step)
                if step_data is None:
                    break
                if step == "review":
                    continue
                f = self.get_form(step=step, data=step_data, files=step_files)
                if not f.is_valid():
                    # jump back to the first invalid visited step
                    self.storage.current_step = step
                    return self.render(f)
                completed.append(f)
            return self.done(completed)

        # Normal flow (Next, Back, step links): let the base class handle it
        return super().post(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        bike_form = next((f for f in form_list if isinstance(f, BikeForm)), None)
        assert bike_form is not None

        # Save bike with owner once
        bike = bike_form.save(commit=False)
        bike.owner = self.request.user
        bike.save()

        # Gallery files from first step
        bike_files = self.storage.get_step_files("bike") or {}
        getlist = getattr(bike_files, "getlist", None)
        gallery_files = getlist("gallery") if getlist else []
        for f in gallery_files:
            LLBikeImg.objects.create(llbike=bike, bike_img=f)

        # Save component forms with FK if they have any data
        component_map = {
            LLComponentSus: ComponentsFormSus,
            LLComponentWheel: ComponentsFormWheel,
            LLComponentDrive: ComponentsFormDrive,
            LLComponentCockpit: ComponentsFormCockpit,
            LLComponentBrakes: ComponentsFormBrakes,
            LLComponentSeat: ComponentsFormSeat,
        }
        for f in form_list:
            for Model, FormCls in component_map.items():
                if isinstance(f, FormCls) and self._has_any_value(f):
                    obj = f.save(commit=False)
                    obj.llbike = bike
                    obj.save()

        return redirect("bikedash:bikedash")


class BikeEditWizard(BikeCreateWizard):
    """
    Same steps/templates as create, but bound to existing objects.
    - 'bike' step edits the LLBike instance (cover image can be replaced).
    - Gallery uploads are appended as new LLBikeImg rows.
    - Component steps edit existing rows if present; otherwise they create new rows on save.
    """

    def dispatch(self, request, *args, **kwargs):
        self._edit_bike = get_object_or_404(LLBike, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_instance(self, step):
        bike = self._edit_bike
        if step == "bike":
            return bike

        mapping = {
            "suspension": LLComponentSus,
            "wheels":     LLComponentWheel,
            "drivetrain": LLComponentDrive,
            "cockpit":    LLComponentCockpit,
            "brakes":     LLComponentBrakes,
            "seat":       LLComponentSeat,
        }
        Model = mapping.get(step)
        if not Model:
            return None

        try:
            # If user has exactly one record per section (your current design)
            return Model.objects.get(llbike=bike)
        except Model.DoesNotExist:
            # Create an unsaved instance bound to this bike so the form can save it
            return Model(llbike=bike)

    def get_context_data(self, form, **kwargs):
        ctx = super().get_context_data(form=form, **kwargs)
        # Flip the template into "edit mode"
        ctx["edit_mode"] = True
        ctx["page_title"] = "Edit Bike"
        # Button labels used only when edit_mode is true
        ctx["review_submit_label"] = "Save Changes"
        ctx["primary_submit_label"] = "Save & Continue →"   # for non-review steps
        ctx["finish_now_label"] = "Save Now"
        # Optional: if you want the step list to say "Edit <Section>" too
        # (You can keep FRIENDLY_TITLES; no change needed)
        return ctx

    def done(self, form_list, **kwargs):
        """
        Update bike + components; append any new gallery images.
        Assumes your BikeForm includes:
          - cover image: bike_img
          - extra images: gallery (FileField, multiple)
        """
        bike = self._edit_bike

        # Save bike step first
        for f in form_list:
            if isinstance(f, BikeForm):
                f.save()  # updates existing bike (bound via get_form_instance)
                # Add newly uploaded gallery images (append; does not delete old)
                bike_files = self.storage.get_step_files("bike") or {}
                getlist = getattr(bike_files, "getlist", None)
                gallery_files = getlist("gallery") if getlist else []
                for fimg in gallery_files:
                    LLBikeImg.objects.create(llbike=bike, bike_img=fimg)
                break

        # Save non-empty component forms
        component_classes = (
            ComponentsFormSus, ComponentsFormWheel, ComponentsFormDrive,
            ComponentsFormCockpit, ComponentsFormBrakes, ComponentsFormSeat,
        )
        for f in form_list:
            if isinstance(f, component_classes) and self._has_any_value(f):
                obj = f.save(commit=False)
                obj.llbike = bike  # ensure FK set for both update/new
                obj.save()

        return redirect("bikedash:bikedash")



def home(request):
    # recent bikes by creation date (adjust field name to yours)
    recent_bikes = LLBike.objects.order_by("-date_created")[:8]
    # placeholder: integrate bikeaggr later
    recent_deals = []  # replace with queryset from bikeaggr
    return render(request, "ll_buildbike/home.html", {
        "recent_bikes": recent_bikes,
        "recent_deals": recent_deals,
    })