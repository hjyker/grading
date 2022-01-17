from rest_framework import permissions


class PermsRequired(permissions.BasePermission):

    def __init__(self, *perms):
        self.perms = perms

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser:
            return True

        user_perms = user.get_all_permissions()
        return True if user_perms & set(self.perms) else False
