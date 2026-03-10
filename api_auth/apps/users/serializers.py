from rest_framework import serializers
from .models import User, Role, Permission


 
# PERMISSION SERIALIZER
 
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "description"]



# ROLE SERIALIZER
 
class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions"]


 
# REGISTER SERIALIZER
 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password", "password_confirm"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username ya está en uso.")
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        # Removemos password_confirm antes de crear el usuario
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)  # Aplica bcrypt
        user.save()

        # Asignar rol "user" por defecto si existe
        default_role = Role.objects.filter(name="user").first()
        if default_role:
            user.roles.add(default_role)

        return user


   
# USER SERIALIZER (para perfil y respuestas)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "roles", "permissions", "is_active", "created_at", "last_login"
        ]
        read_only_fields = ["id", "email", "is_active", "created_at", "last_login"]

    def get_permissions(self, obj):
        return list(obj.get_all_permissions_codenames())

#Roles Serializer
class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Permission.objects.all(),
        source="permissions",
        required=False
    )

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "permission_ids"]