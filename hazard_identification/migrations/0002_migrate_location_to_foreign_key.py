# Generated migration to convert location field from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


def migrate_location_data(apps, schema_editor):
    """Migrate existing location string data to foreign key references"""
    HazardIdentification = apps.get_model('hazard_identification', 'HazardIdentification')
    Location = apps.get_model('inspection_management', 'Location')
    
    # Get the Dubai location (we just created it)
    try:
        dubai_location = Location.objects.get(name='Dubai')
        
        # Update all existing hazards to use the Dubai location
        HazardIdentification.objects.filter(location='Dubai').update(location_id=dubai_location.id)
        
        print(f"Updated {HazardIdentification.objects.filter(location_id=dubai_location.id).count()} hazards to use Dubai location")
    except Location.DoesNotExist:
        print("Dubai location not found, skipping migration")


def reverse_migrate_location_data(apps, schema_editor):
    """Reverse migration - convert foreign key back to string"""
    HazardIdentification = apps.get_model('hazard_identification', 'HazardIdentification')
    Location = apps.get_model('inspection_management', 'Location')
    
    # Convert location IDs back to location names
    for hazard in HazardIdentification.objects.all():
        if hazard.location_id:
            try:
                location = Location.objects.get(id=hazard.location_id)
                hazard.location = location.name
                hazard.save()
            except Location.DoesNotExist:
                hazard.location = 'Unknown'
                hazard.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hazard_identification', '0001_initial'),
        ('inspection_management', '0001_initial'),
    ]

    operations = [
        # First, add a temporary location_id field
        migrations.AddField(
            model_name='hazardidentification',
            name='location_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        
        # Migrate the data
        migrations.RunPython(migrate_location_data, reverse_migrate_location_data),
        
        # Remove the old location field
        migrations.RemoveField(
            model_name='hazardidentification',
            name='location',
        ),
        
        # Rename location_id to location and make it a proper ForeignKey
        migrations.RenameField(
            model_name='hazardidentification',
            old_name='location_id',
            new_name='location',
        ),
        
        # Make it a proper ForeignKey
        migrations.AlterField(
            model_name='hazardidentification',
            name='location',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='hazards',
                to='inspection_management.location',
                help_text='Specific location where the hazard was found'
            ),
        ),
    ]
