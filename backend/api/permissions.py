from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Доступ разрешен только автору."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user or request.method
                in permissions.SAFE_METHODS)


class IsAuthorOnly(permissions.BasePermission):
    """Доступ разрешен только автору."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
