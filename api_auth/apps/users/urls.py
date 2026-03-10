from django.urls import path
from .views import RegisterView, ProfileView, RoleAssignView, RoleListView, PermissionListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("roles/", RoleListView.as_view(), name="roles"),
    path('permissions/', PermissionListView.as_view(), name='permissions')
]