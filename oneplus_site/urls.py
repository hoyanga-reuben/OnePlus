from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('content.urls')),
    path('chat/', include('chat.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    
    path('accounts/', include('allauth.urls')),
    

    path(
        'accounts/verification-sent/',
        TemplateView.as_view(template_name="account/verification_sent.html"),
        name="account_verification_sent"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
