from django.utils.deprecation import MiddlewareMixin


class TenantIsolationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.factory = None

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = getattr(user, "userprofile", None)
            if profile:
                request.factory = profile.factory
