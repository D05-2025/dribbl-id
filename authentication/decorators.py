from django.shortcuts import redirect
from functools import wraps

def login_required_custom(function=None, login_url='/auth/login/'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user:  # Cek custom user kita
                return redirect(login_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator