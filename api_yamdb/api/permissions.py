from rest_framework import permissions


class Anonim(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True


class IsAuthenticatedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.role == 'user'
                if request.user.is_authenticated else False)

    def has_object_permission(self, request, view, obj):
        return (request.user.role == 'user'
                if request.user.is_authenticated else False)


class Moderator(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'moderator'
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.role == 'moderator'
        else:
            return False


class AdminOrRedOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class Admin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        else:
            return False


class RewiewPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if (request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.role == 'admin'
                     or request.user.role == 'moderator'
                     or request.user.is_superuser)):
            return True
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class CommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated):
            return True

    def has_object_permission(self, request, view, obj):
        if (request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.role == 'admin'
                     or request.user.role == 'moderator'
                     or request.user.is_superuser)):
            return True
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False
