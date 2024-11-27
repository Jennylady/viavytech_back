from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsAuthenticatedWoman(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user and request.user.is_authenticated:
                if request.user.sexe == 'F':
                    request.woman = request.user.woman
                    return True
                else:
                    raise PermissionDenied("Authorization failed: User is not female")
            else:
                raise PermissionDenied("Authorization failed: Client is not female")
        except Exception:
            raise PermissionDenied("Authorization failed: Client is not female")