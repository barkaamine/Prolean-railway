import os
import django
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
django.setup()

from prolean.models import Training

def fix_slugs():
    """Update training slugs to be URL-safe (ASCII-only)"""
    print("🚀 Starting slug repair...")
    trainings = Training.objects.all()
    count = 0
    
    for training in trainings:
        old_slug = training.slug
        new_slug = slugify(training.title)
        
        if old_slug != new_slug:
            print(f"🔄 Fixing: '{old_slug}' -> '{new_slug}'")
            training.slug = new_slug
            training.save()
            count += 1
            
    print(f"✅ Successfully updated {count} slugs.")

if __name__ == "__main__":
    fix_slugs()
