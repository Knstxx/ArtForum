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

class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return ((request.user.is_authenticated
                 and request.user.role == 'admin')
                or request.method in permissions.SAFE_METHODS)

'''
class AdminOrUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'admin'
        )


class IsAuthorModeratorOrReadOnly(permissions.BasePermission):
    """
    Допуск на уровне объекта.
    Изменение только для автора объекта или модератора.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'moderator'
        )
'''