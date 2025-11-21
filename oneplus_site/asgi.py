import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack # Hii huunganisha Session na Cookie

# Lazima uweke settings kwanza
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oneplus_site.settings')

# Inaleta routing pattern kutoka kwenye app ya chat
from chat import routing 

# Hii ndiyo ASGI Application yetu kuu.
# Ni muhimu kupanga safu ya middleware hivi:
# 1. SessionMiddlewareStack
# 2. AuthMiddlewareStack
# 3. URLRouter (routing yetu)
application = ProtocolTypeRouter({
    # Maombi ya kawaida ya HTTP yataelekezwa kwa Django's WSGI (kupitia ASGI wrapper)
    "http": get_asgi_application(),

    # Maombi ya WebSocket yanapitia Session & Auth kabla ya kufikia Consumer
    "websocket": SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})