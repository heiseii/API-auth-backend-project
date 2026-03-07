from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthorizationMiddleware:
    """
    Middleware que verifica el token JWT en cada request.
    
    - Rutas públicas: pasan sin verificación
    - Rutas protegidas: requieren token válido
    - Rutas de admin: requieren is_staff o is_superuser
    """

    # Rutas que no requieren autenticación
    PUBLIC_PATHS = [
        "/api/auth/login/",
        "/api/auth/token/refresh/",
        "/api/users/register/",
        "/api/schema/",
        "/api/docs/",
        "/admin/",
    ]

    # Rutas que requieren ser staff o superuser
    ADMIN_PATHS = [
        "/api/users/roles/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.authenticator = JWTAuthentication()

    def __call__(self, request):
        path = request.path

        # ── Rutas públicas — dejar pasar sin verificar ──
        if self._is_public(path):
            return self.get_response(request)

        # ── Intentar autenticar con JWT ──────────────────
        user = self._authenticate(request)

        if user is None:
            return JsonResponse(
                {"detail": "Autenticación requerida."},
                status=401
            )

        if not user.is_active:
            return JsonResponse(
                {"detail": "Cuenta desactivada."},
                status=403
            )

        # ── Verificar acceso a rutas de admin ────────────
        if self._is_admin_path(path):
            if not (user.is_staff or user.is_superuser):
                return JsonResponse(
                    {"detail": "No tenés permisos para acceder a este recurso."},
                    status=403
                )

        # ── Todo OK — continuar con la request ──────────
        request.user = user
        return self.get_response(request)

    def _authenticate(self, request):
        """Intenta autenticar el request con JWT. Retorna el user o None."""
        try:
            result = self.authenticator.authenticate(request)
            if result is None:
                return None
            user, token = result
            return user
        except (InvalidToken, TokenError):
            return None

    def _is_public(self, path):
        """Verifica si la ruta es pública."""
        return any(path.startswith(public) for public in self.PUBLIC_PATHS)

    def _is_admin_path(self, path):
        """Verifica si la ruta requiere permisos de admin."""
        return any(path.startswith(admin) for admin in self.ADMIN_PATHS)