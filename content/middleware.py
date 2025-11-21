# content/middleware.py

from django.utils import timezone
from django.conf import settings
from datetime import timedelta

class LastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.update_interval = getattr(settings, 'LAST_ACTIVITY_UPDATE_INTERVAL_SECONDS', 300) # 5 minutes

    def __call__(self, request):
        response = self.get_response(request)
        
        # Angalia kama mtumiaji ame-login na siyo Static/Media files request
        if request.user.is_authenticated and request.path.startswith(settings.STATIC_URL) is False:
            
            # Punguza queries: Update mara moja tu kwa kila dakika 5 (300 seconds)
            if (timezone.now() - request.user.last_activity) > timedelta(seconds=self.update_interval):
                request.user.last_activity = timezone.now()
                request.user.save(update_fields=['last_activity'])

        return response