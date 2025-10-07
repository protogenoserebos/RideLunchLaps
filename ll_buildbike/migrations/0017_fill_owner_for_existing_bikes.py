from django.conf import settings
from django.db import migrations

def set_owner_for_existing_bikes(apps, schema_editor):
    # Swappable user model
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    Bike = apps.get_model("ll_buildbike", "LLBike")

    # Create or get a "system" user to own legacy bikes
    # Adjust username/email as you like
    system_user, created = User.objects.get_or_create(
        username="system",
        defaults={"email": "system@ridelunchlaps.com", "is_active": False},
    )
    # If password API exists on this user model, make it unusable
    try:
        system_user.set_unusable_password()
        system_user.save(update_fields=["password"])
    except Exception:
        pass

    # Assign the system user to all bikes that currently have no owner
    Bike.objects.filter(owner__isnull=True).update(owner=system_user)

class Migration(migrations.Migration):

    dependencies = [
        ("ll_buildbike", "0016_llbike_slug_llbike_uniq_bike_slug_per_owner"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(set_owner_for_existing_bikes, migrations.RunPython.noop),
    ]
