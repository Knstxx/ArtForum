from rest_framework import permissions


class IsAdminOrRead(permissions.BasePermission):
    """Полный доступ только у админа."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.role == 'admin':
            return True


class AdminOnly(permissions.BasePermission):
    """Только администратор."""

    def has_permission(self, request, view):
        return (
            request.user.is_admin
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or request.user.is_staff
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Полный доступ для админа модератора или автора."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return (request.user.is_authenticated and (
            request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        ))
