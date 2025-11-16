from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MembershipPayment, MemberProfile  # ✅ Import your models here
from django.conf import settings

@receiver(post_save, sender=MembershipPayment)
def update_member_status(sender, instance, created, **kwargs):
    """
    Whenever a new MembershipPayment is created,
    update or activate the corresponding member's profile.
    """
    if created:
        profile, _ = MemberProfile.objects.get_or_create(user=instance.user)
        profile.last_payment_date = instance.date_paid
        profile.update_membership_status()
        profile.save()



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_member_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = MemberProfile.objects.get_or_create(user=instance)
        profile.generate_control_number()
