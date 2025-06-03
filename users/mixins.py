# users/mixins.py
from django.core.exceptions import PermissionDenied

class OwnershipRequiredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.user_type == 'teacher':
            return qs.filter(teacher=self.request.user)
        return qs