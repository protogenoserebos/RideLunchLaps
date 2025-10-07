from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import LLBike, LLBikeImg


def _delete_file(f):
    try:
        if f and f.name:
            storage = f.storage
            if storage.exists(f.name):
                storage.delete(f.name)
    except Exception:
        # swallow filesystem errors — avoid breaking deletes
        pass

@receiver(post_delete, sender=LLBike)
def delete_cover_on_bike_delete(sender, instance, **kwargs):
    _delete_file(instance.bike_img)

@receiver(post_delete, sender=LLBikeImg)
def delete_gallery_on_row_delete(sender, instance, **kwargs):
    _delete_file(instance.bike_img)

@receiver(pre_save, sender=LLBike)
def delete_old_cover_on_replace(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = LLBike.objects.get(pk=instance.pk)
    except LLBike.DoesNotExist:
        return
    old_file = getattr(old, "bike_img", None)
    new_file = getattr(instance, "bike_img", None)
    if old_file and (not new_file or old_file.name != getattr(new_file, "name", None)):
        _delete_file(old_file)

@receiver(pre_save, sender=LLBikeImg)
def delete_old_gallery_on_replace(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = LLBikeImg.objects.get(pk=instance.pk)
    except LLBikeImg.DoesNotExist:
        return
    old_file = getattr(old, "bike_img", None)
    new_file = getattr(instance, "bike_img", None)
    if old_file and (not new_file or old_file.name != getattr(new_file, "name", None)):
        _delete_file(old_file)
