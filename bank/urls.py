from django.urls import path,include
import bank.views as views

urlpatterns = [
    path('deposit',views.deposit),
    path('withdraw',views.withdraw),
    path('register',views.register),
    path('verificationcode',views.getVerificationCode),
]