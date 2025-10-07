from django import forms


from .models import (
    LLBike, LLComponentSus, LLComponentDrive, LLComponentWheel,
    LLComponentCockpit, LLComponentBrakes, LLComponentSeat, LLBikeImg
)


class MultiFileInput(forms.ClearableFileInput):
    # This is the switch Django checks to allow multiple files
    allow_multiple_selected = True


SUS_FRONTSUS_FIELDS = [
    "bike_frontsus_make", "bike_frontsus_model", "bike_frontsus_travel",
    "bike_frontsus_year", "bike_frontsus_review", "bike_frontsus_addtnotes",
]
SUS_REARSUS_FIELDS = [
    "bike_rearsus_make", "bike_rearsus_model", "bike_rearsus_eyetoeye",
    "bike_rearsus_travel", "bike_rearsus_year", "bike_rearsus_review",
    "bike_rearsus_addtnotes",
]

DRIVE_DERAILLEUR_FIELDS = [
    "bike_derailleur_make", "bike_derailleur_model", "bike_derailleur_year",
    "bike_derailleur_type", "bike_derailleur_review", "bike_derailleur_addtnotes",
]
DRIVE_CASSETTE_FIELDS = [
    "bike_cassette_make", "bike_cassette_model", "bike_cassette_year",
    "bike_cassette_range", "bike_cassette_speed", "bike_cassette_review",
    "bike_cassette_addtnotes",
]
DRIVE_CRANKS_FIELDS = [
    "bike_cranks_make", "bike_cranks_model", "bike_cranks_length",
    "bike_cranks_material", "bike_cranks_review", "bike_cranks_addtnotes",
]
DRIVE_PEDAL_FIELDS = [
    "bike_pedals_make", "bike_pedals_model", "bike_pedals_type",
    "bike_pedals_review", "bike_pedals_addtnotes",
]
DRIVE_CHAINRING_FIELDS = [
    "bike_chainring_make", "bike_chainring_model", "bike_chainring_teeth",
    "bike_chainring_bcd", "bike_chainring_review", "bike_chainring_addtnotes",
]
DRIVE_CHAIN_FIELDS = [
    "bike_chain_make", "bike_chain_model", "bike_chain_speed",
    "bike_chain_review", "bike_chain_addtnotes",
]
DRIVE_BB_FIELDS = [
    "bike_bottombracket_make", "bike_bottombracket_model",
    "bike_bottombracket_fitment", "bike_bottombracket_width",
    "bike_bottombracket_review", "bike_bottombracket_addtnotes",
]

WHEEL_FRONT_TIRE_FIELDS = [
    "bike_fronttire_make", "bike_fronttire_model", "bike_fronttire_width",
    "bike_fronttire_quality", "bike_fronttire_review", "bike_fronttire_addtnotes",
]
WHEEL_REAR_TIRE_FIELDS = [
    "bike_reartire_make", "bike_reartire_model", "bike_reartire_width",
    "bike_reartire_quality", "bike_reartire_review", "bike_reartire_addtnotes",
]
WHEEL_COMPLETE_FIELDS = [
    "bike_complete_wheel_make", "bike_complete_wheel_model",
    "bike_complete_wheel_size", "bike_complete_wheel_type",
    "bike_complete_wheel_review", "bike_complete_wheel_addtnotes",
]
WHEEL_HUB_FIELDS = [
    "bike_hubs_make", "bike_hubs_model", "bike_hubs_eng", "bike_hubs_frontwidth",
    "bike_hubs_rearwidth", "bike_hubs_axle", "bike_hubs_review", "bike_hubs_addtnotes",
]
WHEEL_RIMS_FIELDS = [
    "bike_rims_make", "bike_rims_model", "bike_rims_holecount",
    "bike_rims_material", "bike_rims_size", "bike_rims_review",
    "bike_rims_addtnotes",
]

COCKPIT_GRIPS_FIELDS = ["bike_grips_make", "bike_grips_model", "bike_grips_review", "bike_grips_addtnotes"]
COCKPIT_BARS_FIELDS = [
    "bike_bars_make", "bike_bars_model", "bike_bars_material", "bike_bars_width",
    "bike_bars_rise", "bike_bars_diam", "bike_bars_review", "bike_bars_addtnotes",
]
COCKPIT_LEVER_FIELDS = [
    "bike_dropperlever_make", "bike_dropperlever_model",
    "bike_brakelevers_make", "bike_brakelevers_model",
    "bike_brakelevers_review", "bike_brakelevers_addtnotes",
]
COCKPIT_SHIFTER_FIELDS = [
    "bike_shifter_make", "bike_shifter_model", "bike_shifter_speed",
    "bike_shifter_review", "bike_shifter_addtnotes",
]
COCKPIT_STEM_FIELDS = [
    "bike_stem_make", "bike_stem_model", "bike_stem_length",
    "bike_stem_stack", "bike_stem_opening", "bike_stem_review",
    "bike_stem_addtnotes",
]
COCKPIT_HEADSET_FIELDS = [
    "bike_headset_make", "bike_headset_model", "bike_headset_type",
    "bike_headset_top", "bike_headset_bottom", "bike_headset_review",
    "bike_headset_addtnotes",
]

BRAKES_BRAKE_FIELDS = ["bike_brakes_make", "bike_brakes_model", "bike_brakes_pistons", "bike_brakes_review", "bike_brakes_addtnotes"]
BRAKES_ROTOR_FIELDS = [
    "bike_brakerotor_make", "bike_brakerotor_model",
    "bike_brakerotor_size", "bike_brakerotor_attach",
    "bike_brakerotor_review", "bike_brakerotor_addtnotes",
]
BRAKES_LEVER_FIELDS = ["bike_brakelevers_make", "bike_brakelevers_model", "bike_brakelevers_review", "bike_brakelevers_addtnotes"]
BRAKES_PADS_FIELDS = ["bike_brakepads_makemodel", "bike_brakepads_material", "bike_brakepads_review", "bike_brakepads_addtnotes"]

SEAT_SEATPOST_FIELDS = [
    "bike_seatpost_type", "bike_seatpost_make", "bike_seatpost_model",
    "bike_seatpost_travel", "bike_seatpost_width", "bike_seatpost_review",
    "bike_seatpost_addtnotes",
]
SEAT_SADDLE_FIELDS = ["bike_saddle_make", "bike_saddle_model", "bike_saddle_review", "bike_saddle_addtnotes"]


# ---------- Forms ----------
class BikeForm(forms.ModelForm):
    # extra gallery input (multi)
    gallery = forms.FileField(
        required=False,
        widget=MultiFileInput(attrs={
            "multiple": True,
            "accept": "image/*",
            "data-preview": "true",
        }),
        label="Additional Photos",
    )

    class Meta:
        model = LLBike
        fields = [
            "bike_name", "bike_make", "bike_model",
            "bike_img",      # single cover photo
            "bike_type", "bike_size", "bike_year", "bike_discipline", "bike_build", "is_default",
        ]
        labels = {
            "bike_img": "Cover Photo",
        }
        widgets = {
            "bike_img": forms.ClearableFileInput(attrs={
                "accept": "image/*",
                "data-preview": "true",
            }),
        }


class BikeImagesForm(forms.ModelForm):
    class Meta:
        model = LLBikeImg
        fields = ["bike_img"]


class ComponentsFormSus(forms.ModelForm):
    # class-level aliases for use in __init__
    FRONTSUS_FIELDS = SUS_FRONTSUS_FIELDS
    REARSUS_FIELDS = SUS_REARSUS_FIELDS

    class Meta:
        model = LLComponentSus
        fields = SUS_FRONTSUS_FIELDS + SUS_REARSUS_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.FRONTSUS_FIELDS + self.REARSUS_FIELDS:
            if name in self.fields:
                self.fields[name].required = False


class ComponentsFormDrive(forms.ModelForm):
    DERAILLEUR_FIELDS = DRIVE_DERAILLEUR_FIELDS
    CASSETTE_FIELDS = DRIVE_CASSETTE_FIELDS
    CRANKS_FIELDS = DRIVE_CRANKS_FIELDS
    PEDAL_FIELDS = DRIVE_PEDAL_FIELDS
    CHAINRING_FIELDS = DRIVE_CHAINRING_FIELDS
    CHAIN_FIELDS = DRIVE_CHAIN_FIELDS
    BB_FIELDS = DRIVE_BB_FIELDS

    class Meta:
        model = LLComponentDrive
        fields = (
            DRIVE_DERAILLEUR_FIELDS
            + DRIVE_CASSETTE_FIELDS
            + DRIVE_CHAINRING_FIELDS
            + DRIVE_CHAIN_FIELDS
            + DRIVE_BB_FIELDS
            + DRIVE_CRANKS_FIELDS
            + DRIVE_PEDAL_FIELDS
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional = (
            self.DERAILLEUR_FIELDS
            + self.CASSETTE_FIELDS
            + self.CHAINRING_FIELDS
            + self.CHAIN_FIELDS
            + self.BB_FIELDS
            + self.CRANKS_FIELDS
            + self.PEDAL_FIELDS
        )
        for name in optional:
            if name in self.fields:
                self.fields[name].required = False


class ComponentsFormWheel(forms.ModelForm):
    FRONT_TIRE_FIELDS = WHEEL_FRONT_TIRE_FIELDS
    REAR_TIRE_FIELDS = WHEEL_REAR_TIRE_FIELDS
    COMPLETE_WHEEL_FIELDS = WHEEL_COMPLETE_FIELDS
    HUB_FIELDS = WHEEL_HUB_FIELDS
    RIMS_FIELDS = WHEEL_RIMS_FIELDS

    class Meta:
        model = LLComponentWheel
        fields = (
            WHEEL_FRONT_TIRE_FIELDS
            + WHEEL_REAR_TIRE_FIELDS
            + WHEEL_COMPLETE_FIELDS
            + WHEEL_HUB_FIELDS
            + WHEEL_RIMS_FIELDS
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional = (
            self.FRONT_TIRE_FIELDS
            + self.REAR_TIRE_FIELDS
            + self.COMPLETE_WHEEL_FIELDS
            + self.HUB_FIELDS
            + self.RIMS_FIELDS
        )
        for name in optional:
            if name in self.fields:
                self.fields[name].required = False


class ComponentsFormCockpit(forms.ModelForm):
    GRIPS_FIELDS = COCKPIT_GRIPS_FIELDS
    BARS_FIELDS = COCKPIT_BARS_FIELDS
    LEVER_FIELDS = COCKPIT_LEVER_FIELDS
    SHIFTER_FIELDS = COCKPIT_SHIFTER_FIELDS
    STEM_FIELDS = COCKPIT_STEM_FIELDS
    HEADSET_FIELDS = COCKPIT_HEADSET_FIELDS

    class Meta:
        model = LLComponentCockpit
        fields = (
            COCKPIT_GRIPS_FIELDS
            + COCKPIT_BARS_FIELDS
            + COCKPIT_LEVER_FIELDS
            + COCKPIT_SHIFTER_FIELDS
            + COCKPIT_STEM_FIELDS
            + COCKPIT_HEADSET_FIELDS
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional = (
            self.GRIPS_FIELDS
            + self.BARS_FIELDS
            + self.LEVER_FIELDS
            + self.SHIFTER_FIELDS
            + self.STEM_FIELDS
            + self.HEADSET_FIELDS
        )
        for name in optional:
            if name in self.fields:
                self.fields[name].required = False


class ComponentsFormBrakes(forms.ModelForm):
    BRAKE_FIELDS = BRAKES_BRAKE_FIELDS
    ROTOR_FIELDS = BRAKES_ROTOR_FIELDS
    LEVER_FIELDS = BRAKES_LEVER_FIELDS
    PADS_FIELDS = BRAKES_PADS_FIELDS

    class Meta:
        model = LLComponentBrakes
        fields = BRAKES_BRAKE_FIELDS + BRAKES_ROTOR_FIELDS + BRAKES_LEVER_FIELDS + BRAKES_PADS_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional = self.BRAKE_FIELDS + self.ROTOR_FIELDS + self.LEVER_FIELDS + self.PADS_FIELDS
        for name in optional:
            if name in self.fields:
                self.fields[name].required = False


class ComponentsFormSeat(forms.ModelForm):
    SEATPOST_FIELDS = SEAT_SEATPOST_FIELDS
    SADDLE_FIELDS = SEAT_SADDLE_FIELDS

    class Meta:
        model = LLComponentSeat
        fields = SEAT_SEATPOST_FIELDS + SEAT_SADDLE_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.SEATPOST_FIELDS + self.SADDLE_FIELDS:
            if name in self.fields:
                self.fields[name].required = False
