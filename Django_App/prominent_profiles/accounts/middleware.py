from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity by updating 'last_visit' and 'last_visit_excluding_today'
    fields on the user model.

    For every request where the user is logged in, this middleware updates the 'last_visit' field to
    the current timestamp. Next, it updates 'last_visit_excluding_today' with the timestamp of the
    user's last visit that was not today; this supports the articles added since last visit counters
    system in the Prominent Profiles Dashboard.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            user = request.user

            # Check if the last visit excluding today is either not set or was before today
            if not user.last_visit_excluding_today or user.last_visit_excluding_today.date() < now.date():
                '''This condition ensures that last_visit_excluding_today is updated only if
                   the current day has changed since the last recorded visit.
                   So skips updating this field if there's already been a visit today.'''

                # Update last_visit_excluding_today to the previous value of last_visit
                # only if last_visit was set and was on a previous day
                if user.last_visit and (
                        not user.last_visit_excluding_today or user.last_visit.date() != now.date()):
                    user.last_visit_excluding_today = user.last_visit

            # Update last_visit to now on every authenticated request - point of middleware!
            # Doing this after above (it was before but that logic is flawed)
            # I need to Monitor/Test this new implementation.
            user.last_visit = now

            user.save()
