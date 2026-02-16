from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(
        {
            "username": request.user.username,
            "is_superuser": request.user.is_superuser,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_factory(request):
    if request.factory is None:
        return Response({"factory": None, "message": "No factory assigned to this user."})

    return Response(
        {
            "factory": request.factory.id,
            "factory_name": request.factory.name,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email", "")

    if not username or not password:
        return Response({"detail": "username and password are required."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"detail": "username already exists."}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({"id": user.id, "username": user.username}, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response({"detail": "Logged out (client should delete tokens)."})
