from datetime import date
from django.utils.timezone import now
from .models import MemberProfile
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin

def deactivate_expired_members():
    today = now().date()
    expired_members = MemberProfile.objects.filter(expiry_date__lt=today, is_active_member=True)

    if expired_members.exists():
        count = expired_members.update(is_active_member=False)
        print(f"{count} members have been deactivated due to expired memberships.")
    else:
        print("No expired memberships found.")




def role_required(*allowed_roles):
    """
    Use as a decorator on function views.
    Example: @role_required('admin', 'staff')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            user_role = getattr(request.user, 'ngo_role', None)
            if user_role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You don't have permission to access this page.")
        return _wrapped
    return decorator

class RoleRequiredMixin(AccessMixin):
    """
    Use as a mixin for class-based views.
    Example: class MyView(RoleRequiredMixin, UpdateView): allowed_roles = ('admin',)
    """
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        user_role = getattr(request.user, 'ngo_role', None)
        if request.user.is_superuser or (user_role in self.allowed_roles):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("You don't have permission to access this page.")
