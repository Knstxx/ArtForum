from rest_framework import permissions

'''
class IsAnonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_anonymous


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'moderator'
'''


class IsAdminOrRead(permissions.BasePermission):
    def has_permission(self, request, view):
        return ((request.user.is_authenticated
                 and request.user.role == 'admin')
                or request.method in permissions.SAFE_METHODS)


class IsAdminOrModerOrRead(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return ((request.user.is_authenticated
                 and request.user.role == 'admin')
                or (request.user.is_authenticated
                    and request.user.role == 'moder')
                or request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and obj.author == request.user))


class AdminOnly(permissions.BasePermission):
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


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_admin if request.user.is_authenticated else False


class AdminModeratorAuthorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
