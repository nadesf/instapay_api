from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import ListUsersView, ResetPasswordUserView, LogoutUserView, ActivateUserAccountView, ChangePasswordUserView, UserTransactionView
from api.views import SendCodeToResetPasswordView, SignupUserView, SecurityUserView, EditUserProfilView, PaymentRequest, UserAccountView, LoginForSecondAuthentication



urlpatterns = [
    # L'INSCRIPTION
    path('users/', ListUsersView.as_view()),
    path("signup/", SignupUserView.as_view()),
    path("active_my_account/<str:code_temp>/", ActivateUserAccountView.as_view()),

    # LA CONNEXION 
    path("login/token/", TokenObtainPairView.as_view()),
    path("login/second_authentication/", LoginForSecondAuthentication.as_view()),
    path("tokenrefresh/", TokenRefreshView.as_view()),
    path("ask_for_reset_password/", SendCodeToResetPasswordView.as_view()),
    path("reset_password/", ResetPasswordUserView.as_view()),
    path("change_password/", ChangePasswordUserView.as_view()),
    path("users/profil/", EditUserProfilView.as_view()),
    path("logout/", LogoutUserView.as_view()),

    # LES SECURITE 
    path("users/security/", SecurityUserView.as_view()),

    # LES TRANSACTIONS 
    path("users/transactions/", UserTransactionView.as_view()),
    path("users/payment_request/", PaymentRequest.as_view()),
    
    # LES COMPTES INSTAPAY 
    path("users/accounts/", UserAccountView.as_view())

]

"""
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2MjY3NTA0MSwianRpIjoiMGNlMTMxZGYzY2FiNDA2MTkyOTAzMTJkNGU2ZGZlOTMiLCJ1c2VyX2lkIjo1fQ.CE48QMSdM9k146iyAVFfyz4XUXKK1pTt0_-OCxg6TPQ",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYyNjE4NjQxLCJqdGkiOiI3ZDQ0MmRiZTY5ZDM0OWJjYjMxMGVkZGUwOTA4YzVmNSIsInVzZXJfaWQiOjV9.kEVWnSec4yC4ze6wjMrv9fbLrRbDsCBx_m8l_120Xq4"
}

{
    "email": "nadefabrice83@gmail.com"
}
"""