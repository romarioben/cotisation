from django.urls import path
from . import views


urlpatterns = [
    
    path('login/', views.MyLoginView.as_view(), name="login"),
    path('logout/', views.MyLogoutView.as_view(), name="logout"),
    path('password-change/', views.MyPasswordChangeView.as_view(), name="password_change"),
    path('password_change/done/', views.MyPasswordChangeDoneView.as_view(), name="password_change_done"),
    path('password_reset/', views.MyPasswordResetView.as_view(), name="password_reset"),
    path('password_reset/done/', views.MyPasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', views.MyPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset/done/', views.MyPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    
    #path('registration/', views.MyRegistrationView.as_view(), name="registration"),
    path('verify-email-send/', views.verify_email_send, name="verify-email-send"),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name="verify-email"),
    
    
    
]






# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']