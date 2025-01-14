from django.urls import path,include,re_path
import user.views as views

urlpatterns = [
    path('register', views.register),
    path('reset', views.reset),
    path('list/availble', views.get_user_list_availble),
    path('list',views.get_user_list),
    path('login/<userName>', views.get_login_information),
    path('modify', views.modify_information),
    path('billing', views.billing),
    path('requests', views.requests_list),
    path('requests/<id>', views.handle_requests),
    path('getprivilege', views.require_privilege),
    path('report', views.user_report),
    path('getvip', views.get_vip),
    path('<id>',views.getUserBasicInfo),
    path('facelogin/<userName>', views.get_facelogin_information),
    path('faceupdate/<id>', views.faceupdate),
    re_path(r'^email/(?P<id>[0-9]+)$', views.check_email),
    path('email/reset', views.reset_by_email),
    path('mobile/scan', views.mobile_scan),
    path('mobile/logincode', views.check_scan_verification_code),
]
