from django.db import models

# Create your models here.


class PBBike(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=50)  
    location = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(unique=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.price}"