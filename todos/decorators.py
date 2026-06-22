from django.contrib.auth.decorators import user_passes_test


def staff_required(view_func=None, login_url='/'):
    """
    Decorator that grants access only to users with is_staff=True.
    Non-authenticated users are redirected to `login_url`.
    Non-staff authenticated users are redirected to `login_url` as well.

    Usage:
        @staff_required
        def my_view(request): ...

        # or with a custom redirect:
        @staff_required(login_url='/login/')
        def my_view(request): ...
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
    )
    if view_func:
        # Called as @staff_required (without parentheses)
        return actual_decorator(view_func)
    # Called as @staff_required(...) (with parentheses)
    return actual_decorator
