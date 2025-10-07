from django.conf import settings
from django.db import models
from ll_buildbike.models import LLBike

class BikeConfig(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="configs")
    bike = models.ForeignKey(LLBike, on_delete=models.CASCADE, related_name="configs")

    # Common settings (you can expand these or move to JSON)
    fork_pressure_psi = models.PositiveIntegerField(null=True, blank=True)
    fork_rebound_clicks = models.PositiveIntegerField(null=True, blank=True)
    shock_pressure_psi = models.PositiveIntegerField(null=True, blank=True)
    shock_rebound_clicks = models.PositiveIntegerField(null=True, blank=True)
    tire_front_psi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tire_rear_psi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    sections = models.JSONField(default=dict, blank=True)  # user-defined dynamic sections later
    is_public = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated", "-created"]

    def __str__(self):
        return f"{self.bike} config by {self.owner}"