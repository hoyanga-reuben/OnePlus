from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MemberProfile
from django.conf import settings

# ----------------- MemberProfile Creation Signal -----------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_member_profile(sender, instance, created, **kwargs):
    """
    Hutengeneza MemberProfile na control number ya kipekee kila mtumiaji mpya anapoundwa.
    """
    if created:
        try:
            profile, _ = MemberProfile.objects.get_or_create(user=instance)
            profile.generate_control_number()
        except Exception as e:
            # Logging any error during profile creation for security/debugging
            print(f"Error creating MemberProfile or Control Number for user {instance.username}: {e}")

# ----------------- IMPORTANT CHANGE -----------------
# Signal ya 'update_member_status' imeondolewa kwa sababu sasa uhakiki wa malipo (verification) 
# unafanywa kwa MIKONO (manual) na Admin/Muhasibu pekee.
# Mabadiliko ya hadhi ya uanachama hufanywa ndani ya verify_payment view.