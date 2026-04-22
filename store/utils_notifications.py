from django.contrib.auth.models import User
from .models_notifications import Notification, UserActivity


def create_notification(user, title, message, notification_type='system', link=None):
    """Create a notification for a user"""
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )


def mark_notification_as_read(notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False


def get_unread_notifications_count(user):
    """Get count of unread notifications for user"""
    return Notification.objects.filter(user=user, is_read=False).count()


def get_recent_notifications(user, limit=10):
    """Get recent notifications for user"""
    return Notification.objects.filter(user=user)[:limit]


def notify_order_created(user, order):
    """Notify user about new order"""
    return create_notification(
        user=user,
        title='Order Placed',
        message=f'Your order #{order.id} has been placed successfully.',
        notification_type='order',
        link=f'/orders/{order.id}/'
    )


def notify_payment_received(user, order):
    """Notify user about payment confirmation"""
    return create_notification(
        user=user,
        title='Payment Confirmed',
        message=f'Payment for order #{order.id} has been received.',
        notification_type='payment',
        link=f'/orders/{order.id}/'
    )


def notify_order_shipped(user, order):
    """Notify user about order shipment"""
    return create_notification(
        user=user,
        title='Order Shipped',
        message=f'Your order #{order.id} has been shipped!',
        notification_type='shipping',
        link=f'/orders/{order.id}/'
    )


def notify_low_stock_admin(product):
    """Notify admin about low stock"""
    from django.contrib.auth.models import User
    admins = User.objects.filter(is_superuser=True)
    
    for admin in admins:
        create_notification(
            user=admin,
            title='Low Stock Alert',
            message=f'Product "{product.name}" is running low on stock ({product.stock} remaining).',
            notification_type='system',
            link=f'/admin/edit-product/{product.id}/'
        )


def log_user_activity(user, activity_type, description, ip_address=None):
    """Log user activity"""
    return UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address
    )


def notify_all_users(title, message, notification_type='promo', link=None):
    """Send notification to all users (for promotions/announcements)"""
    users = User.objects.filter(is_active=True, is_superuser=False)
    notifications = []
    
    for user in users:
        notifications.append(
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                link=link
            )
        )
    
    # Bulk create notifications
    Notification.objects.bulk_create(notifications)
    return len(notifications)
