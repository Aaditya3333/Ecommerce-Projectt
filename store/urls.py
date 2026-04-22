from django.urls import path
from . import views
from . import views_admin
from . import views_checkout
from . import views_reviews
from . import views_search
from . import views_notifications
from . import views_comparison
from . import views_recent
from . import views_analytics
from . import views_wishlist
from . import views_payment
from . import views_newsletter
from . import views_social
from . import views_recommendations
from . import views_voice
from . import views_advanced_analytics
from . import views_advanced_search
from . import views_loyalty
from . import views_ai_recommendations
from . import views_virtual_try_on
from . import views_voice_shopping
from . import views_chatbot

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('category/<int:pk>/', views.category_products, name='category_products'),
    
    # Checkout URLs
    path('checkout/', views_checkout.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views_checkout.order_confirmation, name='order_confirmation'),
    path('order-detail/<int:order_id>/', views_checkout.order_detail, name='order_detail'),
    
    # Review URLs
    path('add-review/<int:product_id>/', views_reviews.add_review, name='add_review'),
    path('product-reviews/<int:product_id>/', views_reviews.product_reviews, name='product_reviews'),
    path('mark-helpful/<int:review_id>/', views_reviews.mark_review_helpful, name='mark_review_helpful'),
    
    # Search URLs
    path('search/', views_search.search, name='search'),
    path('search-suggestions/', views_search.search_suggestions, name='search_suggestions'),
    
    # Comparison URLs
    path('compare/', views_comparison.comparison_page, name='comparison'),
    path('add-to-comparison/', views_comparison.add_to_comparison, name='add_to_comparison'),
    path('remove-from-comparison/', views_comparison.remove_from_comparison, name='remove_from_comparison'),
    path('clear-comparison/', views_comparison.clear_comparison, name='clear_comparison'),
    path('comparison-count/', views_comparison.get_comparison_count, name='comparison_count'),
    
    # Recently Viewed URLs
    path('recently-viewed/', views_recent.recently_viewed, name='recently_viewed'),
    path('clear-recently-viewed/', views_recent.clear_recently_viewed, name='clear_recently_viewed'),
    
    # Analytics URLs
    path('dashboard/', views_analytics.sales_dashboard, name='sales_dashboard'),
    path('product-analytics/', views_analytics.product_analytics, name='product_analytics'),
    
    # Wishlist URLs
    path('wishlist/', views_wishlist.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views_wishlist.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views_wishlist.remove_from_wishlist, name='remove_from_wishlist'),
    path('clear-wishlist/', views_wishlist.clear_wishlist, name='clear_wishlist'),
    path('move-to-cart/<int:product_id>/', views_wishlist.move_to_cart, name='move_to_cart'),
    path('wishlist-count/', views_wishlist.get_wishlist_count, name='wishlist_count'),
    
    # Payment URLs
    path('payment/<int:order_id>/', views_payment.payment_page, name='payment_page'),
    path('create-payment-intent/<int:order_id>/', views_payment.create_payment_intent, name='create_payment_intent'),
    path('payment-success/<int:order_id>/', views_payment.payment_success, name='payment_success'),
    path('payment-cancelled/<int:order_id>/', views_payment.payment_cancelled, name='payment_cancelled'),
    path('stripe-webhook/', views_payment.stripe_webhook, name='stripe_webhook'),
    path('paypal-payment/<int:order_id>/', views_payment.paypal_payment, name='paypal_payment'),
    path('digital-wallet-payment/<int:order_id>/', views_payment.digital_wallet_payment, name='digital_wallet_payment'),
    
    # Newsletter URLs
    path('newsletter-signup/', views_newsletter.newsletter_signup, name='newsletter_signup'),
    path('newsletter-unsubscribe/', views_newsletter.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('send-promotional-email/', views_newsletter.send_promotional_email, name='send_promotional_email'),
    path('newsletter-management/', views_newsletter.newsletter_management, name='newsletter_management'),
    
    # Social URLs
    path('social-share/<int:product_id>/<str:platform>/', views_social.social_share, name='social_share'),
    path('social-stats/<int:product_id>/', views_social.get_social_stats, name='social_stats'),
    path('social-login/<str:platform>/', views_social.social_login_redirect, name='social_login'),
    path('social-callback/<str:platform>/', views_social.social_callback, name='social_callback'),
    
    # Recommendation URLs
    path('recommendations/<int:product_id>/', views_recommendations.product_recommendations, name='product_recommendations'),
    path('recommendations/', views_recommendations.product_recommendations, name='general_recommendations'),
    path('recommendation-widget/', views_recommendations.recommendation_widget, name='recommendation_widget'),
    path('personalized-dashboard/', views_recommendations.personalized_dashboard, name='personalized_dashboard'),
    
    # Voice Search URLs
    path('voice-search/', views_voice.voice_search_api, name='voice_search_api'),
    path('voice-search-page/', views_voice.voice_search_page, name='voice_search_page'),
    path('test-voice/', views_voice.test_voice_page, name='test_voice_page'),
    path('voice-commands-page/', views_voice.voice_commands_page, name='voice_commands_page'),
    path('voice-suggestions/', views_voice.voice_suggestions, name='voice_suggestions'),
    path('voice-commands/', views_voice.voice_commands, name='voice_commands'),
    
    # Advanced Search URLs
    path('search/', views_advanced_search.advanced_search, name='advanced_search'),
    path('search/autocomplete/', views_advanced_search.autocomplete_search, name='search_autocomplete'),
    path('search/suggestions/', views_advanced_search.search_suggestions_api, name='search_suggestions_api'),
    path('search/popular/', views_advanced_search.popular_searches, name='popular_searches'),
    path('search/history/', views_advanced_search.search_history, name='search_history'),
    path('search/save/', views_advanced_search.save_search, name='save_search'),
    
    # Loyalty Program URLs
    path('loyalty/', views_loyalty.loyalty_dashboard, name='loyalty_dashboard'),
    path('loyalty/tiers/', views_loyalty.loyalty_tiers, name='loyalty_tiers'),
    path('loyalty/history/', views_loyalty.points_history, name='loyalty_history'),
    path('loyalty/refer/', views_loyalty.referral_program, name='loyalty_referral'),
    path('loyalty/earn/', views_loyalty.earn_points_opportunities, name='loyalty_earn_points'),
    path('loyalty/redeem/<int:reward_id>/', views_loyalty.redeem_reward, name='loyalty_redeem_reward'),
    path('loyalty/api/', views_loyalty.loyalty_api_data, name='loyalty_api'),
    
    # Advanced Analytics URLs
    path('advanced-analytics/', views_advanced_analytics.advanced_analytics_dashboard, name='advanced_analytics'),
    path('analytics-api-data/', views_advanced_analytics.analytics_api_data, name='analytics_api_data'),
    path('export-analytics/', views_advanced_analytics.export_analytics, name='export_analytics'),
    
    # Chatbot URLs
    path('chatbot/', views_chatbot.chatbot_page, name='chatbot_page'),
    path('chatbot-api/', views_chatbot.chatbot_api, name='chatbot_api'),
    path('chatbot-history/', views_chatbot.chatbot_history, name='chatbot_history'),
    path('chatbot-analytics/', views_chatbot.chatbot_analytics, name='chatbot_analytics'),
    
    # AI Recommendations URLs
    path('ai/track-behavior/', views_ai_recommendations.track_user_behavior, name='ai_track_behavior'),
    path('ai/recommendations/', views_ai_recommendations.get_recommendations, name='ai_recommendations'),
    path('ai/trending/', views_ai_recommendations.trending_products_ai, name='ai_trending'),
    path('ai/personalization/', views_ai_recommendations.personalization_dashboard, name='ai_personalization'),
    path('ai/search/', views_ai_recommendations.ai_search_assistant, name='ai_search'),
    
    # Virtual Try-On URLs
    path('virtual-try-on/<int:product_id>/', views_virtual_try_on.virtual_try_on_page, name='virtual_try_on'),
    path('virtual-try-on/upload/', views_virtual_try_on.upload_user_image, name='virtual_try_on_upload'),
    path('virtual-try-on/my-try-ons/', views_virtual_try_on.my_virtual_try_ons, name='my_virtual_try_ons'),
    path('virtual-try-on/analytics/', views_virtual_try_on.virtual_try_on_analytics, name='virtual_try_on_analytics'),
    path('virtual-try-on/feedback/', views_virtual_try_on.virtual_try_on_feedback, name='virtual_try_on_feedback'),
    
    # AR Product URLs
    path('ar/<int:product_id>/', views_virtual_try_on.ar_product_viewer, name='ar_product_viewer'),
    path('ar/qr-code/<int:product_id>/', views_virtual_try_on.ar_qr_code_generator, name='ar_qr_code'),
    
    # Voice Shopping URLs
    path('voice-shopping/', views_voice_shopping.voice_shopping_assistant, name='voice_shopping'),
    path('voice-shopping/command/', views_voice_shopping.voice_command_processor, name='voice_command'),
    path('voice-shopping/analytics/', views_voice_shopping.voice_session_analytics, name='voice_analytics'),
    
    # Admin URLs
    path('admin/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin/categories/', views_admin.admin_categories, name='admin_categories'),
    path('admin/products/', views_admin.admin_products, name='admin_products'),
    path('admin/create-category/', views_admin.admin_create_category, name='admin_create_category'),
    path('admin/create-product/', views_admin.admin_create_product, name='admin_create_product'),
    path('admin/edit-category/<int:category_id>/', views_admin.admin_edit_category, name='admin_edit_category'),
    path('admin/delete-category/<int:category_id>/', views_admin.admin_delete_category, name='admin_delete_category'),
    path('admin/edit-product/<int:product_id>/', views_admin.admin_edit_product, name='admin_edit_product'),
    path('admin/delete-product/<int:product_id>/', views_admin.admin_delete_product, name='admin_delete_product'),
    path('admin/export-products/', views_admin.admin_export_products, name='admin_export_products'),
    path('admin/import-products/', views_admin.admin_import_products, name='admin_import_products'),
    
    # Order Tracking & Management URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/return/', views.request_return, name='request_return'),
    path('track-order/', views.track_order, name='track_order'),
    
    # User Address Book URLs
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    
    # Coupon System URLs
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    
    # Enhanced User Dashboard
    path('my-dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Notifications URLs
    path('notifications/', views_notifications.notifications_list, name='notifications_list'),
    path('notifications/api/', views_notifications.notifications_api, name='notifications_api'),
    path('notifications/mark-read/<int:notification_id>/', views_notifications.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views_notifications.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/dropdown/', views_notifications.notification_dropdown, name='notification_dropdown'),
]
