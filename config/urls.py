from django.contrib import admin
from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    title="IoT Platform API",
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="jwt_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.devices.urls")),
    path("api/schema/", schema_view, name="api-schema"),
]
