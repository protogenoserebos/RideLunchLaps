from django import forms
from .models import BikeConfig

class BikeConfigForm(forms.ModelForm):
    class Meta:
        model = BikeConfig
        fields = [
            "bike",
            "fork_pressure_psi","fork_rebound_clicks",
            "shock_pressure_psi","shock_rebound_clicks",
            "tire_front_psi","tire_rear_psi",
            "is_public",
        ]