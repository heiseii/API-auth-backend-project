from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

 
# PERMISSION

class Permission(models.Model):
    """
    Permiso individual. Ej: 'can_delete_users', 'can_view_reports'
    Se crean dinámicamente desde la base de datos.
    """
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "permissions"
        ordering = ["name"]

    def __str__(self):
        return self.codename


 
# ROLE
 
class Role(models.Model):
    """
    Rol que agrupa permisos. Ej: 'admin', 'moderator', 'user'
    Un usuario puede tener múltiples roles.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.name



# CUSTOM USER MANAGER
 
class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        if not username:
            raise ValueError("El username es obligatorio")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Aplica bcrypt automáticamente
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, username, password, **extra_fields)


 
# CUSTOM USER
 
class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario custom. Usa email como identificador principal.
    Incluye campos para bloqueo por intentos fallidos.
    """

    # Campos principales
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    # Roles dinámicos
    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name="users"
    )

    # Flags de Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Bloqueo por intentos fallidos 
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    # Métodos de bloqueo 
    def is_locked(self):
        """Retorna True si la cuenta está bloqueada en este momento."""
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    def register_failed_attempt(self, max_attempts, lockout_minutes):
        """
        Incrementa el contador de intentos fallidos.
        Si supera el máximo, bloquea la cuenta.
        """
        self.failed_attempts += 1
        if self.failed_attempts >= max_attempts:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lockout_minutes)
        self.save(update_fields=["failed_attempts", "locked_until"])

    def reset_failed_attempts(self):
        """Resetea el contador tras un login exitoso."""
        self.failed_attempts = 0
        self.locked_until = None
        self.save(update_fields=["failed_attempts", "locked_until"])

    #  Métodos de permisos dinámicos 
    def get_all_permissions_codenames(self):
        """Retorna un set con todos los codenames de permisos del usuario."""
        return set(
            Permission.objects.filter(roles__users=self)
            .values_list("codename", flat=True)
        )

    def has_permission(self, codename):
        """Verifica si el usuario tiene un permiso específico."""
        if self.is_superuser:
            return True
        return codename in self.get_all_permissions_codenames()

    def get_roles_names(self):
        """Retorna una lista con los nombres de roles del usuario."""
        return list(self.roles.values_list("name", flat=True))