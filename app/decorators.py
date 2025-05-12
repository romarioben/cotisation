from django.http import HttpResponseForbidden

def permission_role(permission_list=[]):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            if request.user.role in permission_list:
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponseForbidden(f"Vous n'êtes pas autorisé(e)")
        return wrapper
    return decorator