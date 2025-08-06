from django.conf import settings
from django.utils.translation import gettext_lazy as _
from functools import wraps


def environment_callback(request):
    """Display environment badge in Unfold Admin"""
    if settings.DEBUG:
        return [_("Development"), "primary"]
    return [_("Production"), "primary"]


def user_has_model_permission(
    user,
    app_label: str,
    model_name: str,
    perm_types=("view", "change", "add", "delete"),
) -> bool:
    """Check if user has any of the specified permissions for a model"""
    if user.is_superuser:
        return True
    
    for perm_type in perm_types:
        perm_code = f"{app_label}.{perm_type}_{model_name}"
        if user.has_perm(perm_code):
            return True
    
    return False


def use_celery(func):
    """Decorator to conditionally use Celery based on USE_CELERY setting"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if settings.USE_CELERY:
            return func.delay(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper