from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
# Create your models here.

from branches.models import State, Zone, Branch, AcademicDevision

# def user_profile_images(instance, filename):
#     return 'pics/user_profile/photos/{}.webp'.format(uuid.uuid4().hex)

class UserProfile(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.PROTECT)
    # photo = WEBPField(upload_to=user_profile_images, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,15}$', message="Phone number must be entered in the format: '+919999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, null=True, blank=True)

    states = models.ManyToManyField(State, related_name="user_states", blank=True)
    zones = models.ManyToManyField(Zone, related_name="user_zones", blank=True)
    branches  = models.ManyToManyField(Branch, related_name="user_locations", blank=True)
    must_change_password = models.BooleanField(default=True)

    academic_devisions = models.ManyToManyField(AcademicDevision, related_name='user_academic_division', blank=True)


    
    def __str__(self):
        return self.user.username

    def clean(self):
        if self.phone_number:
            qs = UserProfile.objects.filter(phone_number=self.phone_number)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({"phone_number": "Phone number must be unique."})

    def save(self, *args, **kwargs):
        self.full_clean()  # this will call clean()
        super().save(*args, **kwargs)

    # @property
    # def imageURL(self):
    #     try:
    #         url = self.photo.url
    #     except ValueError:
    #         url = ''
    #     return url

@receiver(post_save, sender=User) 
def create_or_update_user_profile(sender, instance, created, **kwargs): 
    if created: 
        UserProfile.objects.create(user=instance) 
    else: 
        # Ensure the user always has a profile, even if it's missing after creation 
        UserProfile.objects.get_or_create(user=instance) # Update user profile if the user is updated 
    instance.userprofile.save()

@receiver(pre_save, sender=User)
def update_user_profile(sender, instance, **kwargs):
    if instance.pk:
        try:
            user_profile = instance.userprofile
            user_profile.save()
        except UserProfile.DoesNotExist:
            pass