from .models import CustomUser

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only override if Django's auth hasn't set a user
        if not hasattr(request, 'user') or request.user.is_anonymous:
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    request.user = CustomUser.objects.get(id=user_id)
                except CustomUser.DoesNotExist:
                    request.user = None

        response = self.get_response(request)
        return response