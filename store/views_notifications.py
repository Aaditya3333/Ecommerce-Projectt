from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .utils_notifications import (
    get_recent_notifications, 
    get_unread_notifications_count,
    mark_notification_as_read,
    create_notification
)


@login_required
def notifications_list(request):
    """Display all notifications for user"""
    notifications = get_recent_notifications(request.user, limit=50)
    unread_count = get_unread_notifications_count(request.user)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'store/notifications/list.html', context)


@login_required
def notifications_api(request):
    """API endpoint for notifications"""
    unread_count = get_unread_notifications_count(request.user)
    recent = get_recent_notifications(request.user, limit=5)
    
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'created': n.created.isoformat(),
                'link': n.link,
            }
            for n in recent
        ]
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    success = mark_notification_as_read(notification_id)
    return JsonResponse({'success': success})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    from .models_notifications import Notification
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def notification_dropdown(request):
    """Render notification dropdown content"""
    notifications = get_recent_notifications(request.user, limit=5)
    unread_count = get_unread_notifications_count(request.user)
    
    return render(request, 'store/notifications/dropdown.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })
