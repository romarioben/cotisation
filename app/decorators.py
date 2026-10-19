from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login


def permission_role(permission_list=None):
    """Autorise les utilisateurs dont le rôle est dans permission_list,
    ainsi que tous ceux qui ont accès à l'espace admin (is_staff / is_superuser)."""
    permission_list = permission_list or []

    def decorator(view_function):
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if user.is_staff or user.is_superuser or getattr(user, "role", None) in permission_list:
                return view_function(request, *args, **kwargs)
            return HttpResponseForbidden("Vous n'êtes pas autorisé(e)")
        return wrapper
    return decorator