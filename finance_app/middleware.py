from django.shortcuts import redirect
from .utils.jwt_utils import verify_jwt

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard"):
            token = request.COOKIES.get("jwt_token")
            if not token or not verify_jwt(token):
                return redirect("login")
        return self.get_response(request)
