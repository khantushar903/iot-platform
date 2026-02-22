from django.utils.deprecation import MiddlewareMixin

from apps.accounts.models import UserProfile


class TenantIsolationMiddleware(MiddlewareMixin):
    """
    Optional convenience middleware.

    With JWT, DRF authentication happens after Django middleware.
    So this middleware may not see an authenticated user.

    DO NOT rely on request.factory for security decisions.
    Always enforce tenant filtering using request.user.userprofile.factory
    inside views/services.
    """

    def process_request(self, request):
        request.factory = None

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return

        try:
            profile = UserProfile.objects.select_related("factory").get(user=user)
            request.factory = profile.factory
        except UserProfile.DoesNotExist:
            pass
