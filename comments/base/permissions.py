from rest_framework import permissions


class HasChildrenPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method != 'DELETE' or not obj.children.exists()
