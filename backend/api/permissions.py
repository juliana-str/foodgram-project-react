from rest_framework import permissions

#
# class IsAdmin(permissions.BasePermission):
#     """Доступ разрешен только администраторам."""
#     def has_permission(self, request, view):
#         return (request.user.is_authenticated
#                 and request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ разрешен только администраторам."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_admin
                    or obj.author == request.user))