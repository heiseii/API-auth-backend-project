from django.urls import path
from .views import RegisterView, ProfileView, UserListView, RoleListView, RoleAssignView, PermissionListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("", UserListView.as_view(), name="user-list"),
    path("roles/", RoleListView.as_view(), name="roles"),
    path("roles/<int:role_id>/assign/", RoleAssignView.as_view(), name="role-assign"),
    path("permissions/", PermissionListView.as_view(), name="permissions"),
]