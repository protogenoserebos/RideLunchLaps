import uuid
from django.urls import reverse
from django.db import models
from django.conf import settings
from .utils.images import compress_image_file
from django.utils.text import slugify


# Create your models here.

    
class LLBike(models.Model):
    """Bike built with the bike editor."""

    Bike_Types = {
        "MTB": "Mountain",
        "E-MTB": "Electric Mountain",
        "Gravel": "Gravel",
        "Road": "Road",
        "DJ": "Dirt Jumper",
    }

    Bike_Disc = {
        "XC": "Cross-Country",
        "Trail": "Trail",
        "Enduro": "Enduro",
        "DH":"Downhill",
        "Park":"Park",
        "Gravel": "Gravel",
        "Road": "Road",
        "DJ": "Dirt Jumper",
    }

    Bike_Build = {
        "Stock": "Stock",
        "Upgraded": "Upgraded",
        "GroundUpBuild": "Ground Up Build",
        "PartsBike":"Parts Bike",
    }

    Bike_Size = {
        "ExtraSmall" : "Extra Small",
        "Small": "Small",
        "Medium": "Medium",
        "Large": "Large",
        "ExtraLarge":"Extra Large",
    }

    bike_size = models.CharField("Bike Size", max_length=30, choices=Bike_Size, blank=True, null=True, help_text="What size is your bike?")
    bike_build = models.CharField("Bike Build", max_length=30, choices=Bike_Build, blank=True, null=True, help_text="What is the build type of your bike?")
    bike_name = models.CharField("Bike Name", max_length=100, blank=True, help_text="What is the name of your bike?")
    bike_make = models.CharField("Bike Make", max_length=100, blank=True, help_text="What is the make of your bike?")
    bike_model = models.CharField("Bike Model", max_length=100, blank=True, help_text="What is the model of your bike?")
    bike_year = models.PositiveIntegerField("Bike Year", blank=True, null=True, help_text="What year is your bike?")
    bike_discipline = models.CharField("Bike Discipline", max_length=30, choices=Bike_Disc, blank=True, null=True, help_text="What type of trails does this bike excel at?")
    bike_type = models.CharField("Bike Type", max_length=30, choices=Bike_Types, blank=True, null=True, help_text="What type of bike is it?")
    date_created = models.DateTimeField(auto_now_add=True)
    bike_img = models.ImageField(upload_to='bike_images/', blank=True, null=True)

    is_default = models.BooleanField("Make this bike the default?", default=False, db_index=True)

    def _slug_base(self):
        # sensible base from name or make/model/year
        parts = []
        if self.bike_name:
            parts.append(self.bike_name)
        else:
            parts += filter(None, [self.bike_make, self.bike_model, str(self.bike_year or "")])
        base = slugify("-".join(parts))[:100]  # leave room for “-99”
        return base or f"bike-{self.public_id.hex[:6]}"

    def _unique_slug_for_owner(self, base):
        # ensure uniqueness per owner by suffixing -2, -3, ...
        slug = base
        if not self.owner_id:
            return slug  # will be re-saved once owner is set (your wizard sets owner before save)
        taken = set(
            LLBike.objects.filter(owner=self.owner, slug__startswith=base)
            .exclude(pk=self.pk)
            .values_list("slug", flat=True)
        )
        if slug not in taken:
            return slug
        i = 2
        while True:
            candidate = f"{base}-{i}"
            if candidate not in taken:
                return candidate
            i += 1

    def save(self, *args, **kwargs):
        # assign a slug once (or when owner changes and slug is empty)
        if not self.slug:
            base = self._slug_base()
            self.slug = self._unique_slug_for_owner(base)
        super().save(*args, **kwargs)
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bikes", null=True, blank=True)
    # pretty URL bit — unique only within the same owner
    slug = models.SlugField(max_length=120, blank=True)
    # keep your shareable fallback URL
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    like_count = models.PositiveIntegerField(default=0)  # denormalized counter

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "slug"], name="uniq_bike_slug_per_owner"),
        ]
        unique_together = (("bike_name", "bike_make", "bike_model", "bike_year"),)  # keep if you already had this

    def __str__(self):
        return self.bike_name or f"Bike {self.pk}"

    def get_absolute_url(self):
        # prefer pretty URL if we have both owner + slug; fallback to public_id route
        if self.slug and self.owner_id:
            return reverse("bikeprofile:detail", kwargs={
                "username": self.owner.username,
                "slug": self.slug,
            })
        return reverse("bikeprofile:detail_public", kwargs={"public_id": self.public_id})
    
class BikeLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name="likes")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "bike")  # prevents multiple likes by the same user

    def __str__(self):
        return f"{self.user} ♥ {self.bike}"

class LLComponentSus(models.Model):
    """Components on a bike."""

    review_choices = {
        '5':'★ ★ ★ ★ ★',
        '4': '★ ★ ★ ★',
        '3': '★ ★ ★',
        '2': '★ ★',
        '1': '★',
    }
# One-to-Many Relationship
    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='suspension_components',
        null=True,
        blank=True,) # Django automatically appends _id for ForeignKey fields
    
# Suspension
    #Front Sus
    bike_frontsus_make = models.CharField("Front Suspension Make", max_length=100, blank=True, help_text="Who makes your fork?")
    bike_frontsus_model = models.CharField("Front Suspension Model", max_length=100, blank=True, help_text="What model is your fork?")
    bike_frontsus_travel = models.CharField("Front Suspension Travel", max_length=100, blank=True, help_text="How much travel does your fork have?")
    bike_frontsus_year = models.PositiveIntegerField(blank=True, null=True, help_text="What year is your fork?") # For integer optional fields, use PositiveIntegerField with blank=True, null=True
    bike_frontsus_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_frontsus_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your front suspension?")
    #Rear Sus
    bike_rearsus_make = models.CharField("Rear Suspension Make", max_length=100, blank=True, help_text="Who makes your rear shock?")
    bike_rearsus_model = models.CharField("Rear Suspension Model", max_length=100, blank=True, help_text="What model is your rear shock?")
    bike_rearsus_eyetoeye = models.CharField("Rear Suspension Eye-to-Eye", max_length=100, blank=True, help_text="What is the eye-to-eye length of your rear shock?")
    bike_rearsus_travel = models.CharField("Rear Suspension Travel", max_length=100, blank=True, help_text="How much travel does your rear shock have?")
    bike_rearsus_year = models.PositiveIntegerField(blank=True, null=True, help_text="What year is your rear shock?") # For integer optional fields, use PositiveIntegerField with blank=True, null=True
    bike_rearsus_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_rearsus_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your rear suspension?")

class LLComponentDrive(models.Model):
    """Drivetrain on a bike."""
    review_choices = {
        '5':'★ ★ ★ ★ ★',
        '4': '★ ★ ★ ★',
        '3': '★ ★ ★',
        '2': '★ ★',
        '1': '★',
    }

    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='drivetrain_components',
        null=True,
        blank=True,) # Django automatically appends _id for ForeignKey fields

# Drivetrain
    # Derailleur
    bike_derailleur_type = models.CharField("Derailleur Type", max_length=100, blank=True, help_text="Ex: Electronic, Mechanical?")
    bike_derailleur_make = models.CharField("Derailleur Make", max_length=100, blank=True, help_text="Who makes your derailleur?")
    bike_derailleur_model = models.CharField("Derailleur Model", max_length=100, blank=True, help_text="What model is your derailleur?")
    bike_derailleur_year = models.PositiveIntegerField("Derailleur Year", blank=True, null=True, help_text="What year is your derailleur?")
    bike_derailleur_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_derailleur_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your derailleur?")
    # Cassette
    bike_cassette_speed = models.PositiveIntegerField("Cassette Speed", blank=True, null=True, help_text="How many speeds (or separate rings) does your cassette have?")
    bike_cassette_make = models.CharField("Cassette Make", max_length=100, blank=True, help_text="Who makes your cassette?")
    bike_cassette_model = models.CharField("Cassette Model", max_length=100, blank=True, help_text="What model is your cassette?")
    bike_cassette_year = models.PositiveIntegerField("Cassette Year", blank=True, null=True, help_text="What year is your cassette?")
    bike_cassette_range = models.CharField("Cassette Range", max_length=100, blank=True, help_text="Range is smallest # of teeth to largest # of teeth (ex: 10-50T).")
    bike_cassette_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_cassette_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your cassette?")

    # Chain
    bike_chain_speed = models.PositiveIntegerField("Chain Speed", blank=True, null=True, help_text="Ex: 9, 10, 11, etc.")
    bike_chain_make = models.CharField("Chain Make", max_length=100, blank=True, help_text="Who makes your chain?")
    bike_chain_model = models.CharField("Chain Model", max_length=100, blank=True, help_text="What model is your chain?")
    bike_chain_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_chain_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your chain?")

    # Chainring
    bike_chainring_make = models.CharField("Chainring Make", max_length=100, blank=True, help_text="Who makes your chainring?")
    bike_chainring_model = models.CharField("Chainring Model", max_length=100, blank=True, help_text="What model is your chainring?")
    bike_chainring_bcd = models.CharField("Chainring BCD", max_length=100, blank=True, help_text="What is the BCD of your chainring?")
    bike_chainring_teeth = models.PositiveIntegerField("Chainring Teeth", blank=True, null=True, help_text="How many teeth does your chainring have?")
    bike_chainring_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_chainring_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your chainring?")

    # Bottom Bracket
    bike_bottombracket_make = models.CharField("Bottom Bracket Make", max_length=100, blank=True, help_text="Who makes your bottom bracket?")
    bike_bottombracket_model = models.CharField("Bottom Bracket Model", max_length=100, blank=True, help_text="What model is your bottom bracket?")
    bike_bottombracket_fitment = models.CharField("Bottom Bracket Fitment", max_length=100, blank=True, help_text="Ex: BSA, Press Fit, etc.")
    bike_bottombracket_width = models.CharField("Bottom Bracket Width (mm)", max_length=100, blank=True, help_text="Ex: 68, 73, etc.")
    bike_bottombracket_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_bottombracket_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your bottom bracket?")

    # Cranks
    bike_cranks_make = models.CharField("Crank Make", max_length=100, blank=True, help_text="Who makes your cranks?")
    bike_cranks_model = models.CharField("Crank Model", max_length=100, blank=True, help_text="What model is your cranks?")
    bike_cranks_length = models.PositiveIntegerField("Crank Length (mm)", blank=True, null=True, help_text="(Ex: 170, 175, etc.)")
    bike_cranks_material = models.CharField("Crank Material", max_length=100, blank=True, help_text="(Ex: Aluminum, Carbon, etc.)")
    bike_cranks_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_cranks_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your cranks?")

    # Pedals
    bike_pedals_type = models.CharField("Pedal Type", max_length=100, blank=True, help_text="Ex: Clipless, Flat, etc.")
    bike_pedals_make = models.CharField("Pedal Make", max_length=100, blank=True, help_text="Who makes your pedals?")
    bike_pedals_model = models.CharField("Pedal Model", max_length=100, blank=True, help_text="What model are your pedals?")
    bike_pedals_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_pedals_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your pedals?")

class LLComponentWheel(models.Model):
    """Wheels on a bike."""

    review_choices = { # Unicode star characters for reviews
        '5':'★ ★ ★ ★ ★',
        '4': '★ ★ ★ ★',
        '3': '★ ★ ★',
        '2': '★ ★',
        '1': '★',
    }

    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='wheel_components',
        null=True,
        blank=True,) # Django automatically appends _id for ForeignKey fields

    # Wheels
    bike_complete_wheel_make = models.CharField(max_length=100, blank=True)
    bike_complete_wheel_model = models.CharField(max_length=100, blank=True)
    bike_complete_wheel_size = models.CharField(max_length=100, blank=True)
    bike_complete_wheel_type = models.CharField(max_length=100, blank=True)
    bike_complete_wheel_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_complete_wheel_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your complete wheel?")

    # Hubs
    bike_hubs_make = models.CharField("Hub Make", max_length=100, blank=True, help_text="Who makes your hubs?")
    bike_hubs_model = models.CharField("Hub Model", max_length=100, blank=True, help_text="What model are your hubs?")
    bike_hubs_frontwidth = models.CharField("Front Hub Width (mm)", max_length=100, blank=True, help_text="Ex: 15 x 110, etc.")
    bike_hubs_rearwidth = models.CharField("Rear Hub Width (mm)", max_length=100, blank=True, help_text="Ex: 12 x 148, etc.")
    bike_hubs_axle = models.CharField("Hub Axle", max_length=100, blank=True, help_text="Ex: Thru Axle, QR, etc.")
    bike_hubs_eng = models.CharField("Rear Hub Engagement", max_length=100, blank=True, help_text="Ex: 36 points, 54 points, etc.")
    bike_hubs_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_hubs_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your hubs?")

    # Rims
    bike_rims_make = models.CharField(max_length=100, blank=True)
    bike_rims_model = models.CharField(max_length=100, blank=True)
    bike_rims_holecount = models.PositiveIntegerField(blank=True, null=True)
    bike_rims_material = models.CharField(max_length=100, blank=True)
    bike_rims_size = models.CharField(max_length=100, blank=True)
    bike_rims_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_rims_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your rims?")

    # Rear Tire
    bike_reartire_make = models.CharField(max_length=100, blank=True)
    bike_reartire_model = models.CharField(max_length=100, blank=True)
    bike_reartire_width = models.CharField(max_length=100, blank=True)
    bike_reartire_quality = models.CharField(max_length=100, blank=True)
    bike_reartire_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_reartire_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your rear tire?")

    # Front Tire
    bike_fronttire_make = models.CharField(max_length=100, blank=True)
    bike_fronttire_model = models.CharField(max_length=100, blank=True)
    bike_fronttire_width = models.CharField(max_length=100, blank=True)
    bike_fronttire_quality = models.CharField(max_length=100, blank=True)
    bike_fronttire_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_fronttire_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your front tire?")

class LLComponentCockpit(models.Model):
    """Cockpit components on a bike."""
    review_choices = {
        '5':'★ ★ ★ ★ ★',
        '4': '★ ★ ★ ★',
        '3': '★ ★ ★',
        '2': '★ ★',
        '1': '★',
    }
    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='cockpit_components',
        null=True,
        blank=True,) # Django automatically appends _id for ForeignKey fields
    # Headset
    bike_headset_make = models.CharField(max_length=100, blank=True)
    bike_headset_model = models.CharField(max_length=100, blank=True)
    bike_headset_type = models.CharField(max_length=100, blank=True)
    bike_headset_top = models.CharField(max_length=100, blank=True)
    bike_headset_bottom = models.CharField(max_length=100, blank=True)
    bike_headset_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_headset_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your headset?")

    # Stem
    bike_stem_make = models.CharField(max_length=100, blank=True)
    bike_stem_model = models.CharField(max_length=100, blank=True)
    bike_stem_length = models.CharField(max_length=100, blank=True)
    bike_stem_stack = models.CharField(max_length=100, blank=True)
    bike_stem_opening = models.CharField(max_length=100, blank=True)
    bike_stem_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_stem_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your stem?")

    # Dropper Lever
    bike_dropperlever_make = models.CharField(max_length=100, blank=True)
    bike_dropperlever_model = models.CharField(max_length=100, blank=True)
    bike_dropperlever_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_dropperlever_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your dropper lever?")

    # Brake Lever
    bike_brakelevers_make = models.CharField(max_length=100, blank=True)
    bike_brakelevers_model = models.CharField(max_length=100, blank=True)
    bike_brakelevers_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_brakelevers_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your brake levers?")

    # Shifter
    bike_shifter_make = models.CharField(max_length=100, blank=True)
    bike_shifter_model = models.CharField(max_length=100, blank=True)
    bike_shifter_speed = models.PositiveIntegerField(blank=True, null=True)
    bike_shifter_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_shifter_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your shifter?")

    # Grips
    bike_grips_make = models.CharField(max_length=100, blank=True)
    bike_grips_model = models.CharField(max_length=100, blank=True)
    bike_grips_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_grips_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your grips?")

    # Bars
    bike_bars_make = models.CharField(max_length=100, blank=True)
    bike_bars_model = models.CharField(max_length=100, blank=True)
    bike_bars_material = models.CharField(max_length=100, blank=True)
    bike_bars_width = models.CharField(max_length=100, blank=True)
    bike_bars_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_bars_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your bars?")
    bike_bars_rise = models.CharField(max_length=100, blank=True)
    bike_bars_diam = models.PositiveIntegerField(blank=True, null=True)

class LLComponentBrakes(models.Model):
    """Brakes on a bike."""
    review_choices = {
        '5':'★ ★ ★ ★ ★',
        '4': '★ ★ ★ ★',
        '3': '★ ★ ★',
        '2': '★ ★',
        '1': '★',
    }
    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='brake_components',
        null=True,
        blank=True,) # Django automatically appends _id for ForeignKey fields
# Brakes
    # Brakes
    bike_brakes_make = models.CharField(max_length=100, blank=True)
    bike_brakes_model = models.CharField(max_length=100, blank=True)
    bike_brakes_pistons = models.PositiveIntegerField(blank=True, null=True)
    bike_brakes_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_brakes_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your brakes?")

    # Rotor
    bike_brakerotor_make = models.CharField(max_length=100, blank=True)
    bike_brakerotor_model = models.CharField(max_length=100, blank=True)
    bike_brakerotor_size = models.PositiveIntegerField(blank=True, null=True)
    bike_brakerotor_attach = models.CharField(max_length=100, blank=True)
    bike_brakerotor_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_brakerotor_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your brake rotor?")

    # Brake Lever
    bike_brakelevers_make = models.CharField(max_length=100, blank=True)
    bike_brakelevers_model = models.CharField(max_length=100, blank=True)
    bike_brakelevers_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_brakelevers_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your brake levers?")

    # Brake Pads
    bike_brakepads_makemodel = models.CharField(max_length=100, blank=True)
    bike_brakepads_material = models.CharField(max_length=100, blank=True)
    bike_brakepads_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_brakepads_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your brake pads?")

class LLComponentSeat(models.Model):
    """Seat and Seatpost on a bike."""
    review_choices = {
        '5':'★ ★ ★ ★ ★',
        '4': '★ ★ ★ ★',
        '3': '★ ★ ★',
        '2': '★ ★',
        '1': '★',
    }
    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='seat_components',
        null=True,
        blank=True,) # Django automatically appends _id for ForeignKey fields
# Seat and Post
    # Seatpost
    bike_seatpost_make = models.CharField(max_length=100, blank=True)
    bike_seatpost_model = models.CharField(max_length=100, blank=True)
    bike_seatpost_travel = models.CharField(max_length=100, blank=True)
    bike_seatpost_type = models.CharField(max_length=100, blank=True)
    bike_seatpost_width = models.CharField(max_length=100, blank=True)
    bike_seatpost_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_seatpost_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your seatpost?")

    # Saddle
    bike_saddle_make = models.CharField(max_length=100, blank=True)
    bike_saddle_model = models.CharField(max_length=100, blank=True)
    bike_saddle_review = models.CharField(max_length=30, choices=review_choices, blank=True, null=True)
    bike_saddle_addtnotes = models.TextField("Additional Notes", max_length=500, blank=True, help_text="Any additional notes about your saddle?")

class LLBikeImg(models.Model):
    llbike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name='bike_images', null=True, blank=True)
    bike_img = models.ImageField(upload_to='bike_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.bike_img and hasattr(self.bike_img, "file") and not getattr(self.bike_img, "_compressed", False):
            self.bike_img.file = compress_image_file(self.bike_img.file)
            self.bike_img.name = self.bike_img.file.name
            setattr(self.bike_img, "_compressed", True)
        super().save(*args, **kwargs)
