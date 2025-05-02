from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.sessions.models import Session
from django.utils import timezone

class SessionControlLoginView(LoginView):
    """
    Custom login view that enforces a single session per user.
    This implementation doesn't require database schema changes.
    """
    def form_valid(self, form):
        """
        Security check complete. Log the user in and handle session control.
        """
        user = form.get_user()
        
        # Make sure the current session is saved
        if not self.request.session.session_key:
            self.request.session.save()
        current_session_key = self.request.session.session_key
        
        # Find any existing sessions for this user
        for session in Session.objects.filter(expire_date__gt=timezone.now()):
            try:
                session_data = session.get_decoded()
                # If this session belongs to our user and it's not the current session
                if (session_data.get('_auth_user_id') == str(user.id) and 
                    session.session_key != current_session_key):
                    # Delete the other session
                    session.delete()
                    messages.warning(self.request, 'نشست قبلی شما خاتمه یافت. شما فقط می‌توانید از یک دستگاه وارد شوید.')
            except Exception:
                # If there's any error decoding the session, just continue
                pass
        
        # Log the user in
        auth_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form) 