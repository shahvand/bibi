from django.contrib.sessions.models import Session
from django.utils import timezone

def session_info(request):
    """
    Adds session information to the context for all templates.
    """
    context = {
        'active_sessions': 0
    }
    
    if request.user.is_authenticated:
        # Count active sessions for this user
        active_count = 0
        for session in Session.objects.filter(expire_date__gt=timezone.now()):
            try:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(request.user.id):
                    active_count += 1
            except:
                pass
                
        context['active_sessions'] = active_count
    
    return context 

def financial_access(request):
    """
    Adds a variable to the context indicating whether the current user
    has access to financial information.
    """
    if not request.user.is_authenticated:
        return {'can_view_financials': False}
    
    return {
        'can_view_financials': request.user.role in ['ACCOUNTANT', 'ADMIN']
    } 