from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.shortcuts import HttpResponse, get_object_or_404, get_list_or_404
from django.contrib.auth import logout

from api.serializers import ListUserSerializer, UserTransactionSerializer, UserAccountSerializer
from api.models import Transactions, Users, Providers, UserAccounts

from myscripts import CodeGenerator, SendMail, HashSecondAuthenticationCode
import threading
import time
from datetime import datetime

# ----------- MES FONCTIONS UTILES --------------#
def Countdown(email_user):

    reason="activate"
    second=30
    time.sleep(second)


    if reason == "activate":
        #time.sleep(second)
        user = get_object_or_404(Users, email=email_user)
        if user.code_temp != "111111":
            Users.objects.delete(user)
    elif reason == "reset_password":
        #time.sleep(20)
        user = get_object_or_404(Users, email=email_user)
        user.code_temp = "111111"
    else:
        pass

def ExecuteTransactionLater():

    date = str(datetime.today()).split(" ")[0]
    transactions = Transactions.objects.filter(state=0)
    for transaction in transactions:
        sender_account = UserAccounts.objects.get(owner=transaction.sender)
        recipient_account = UserAccounts.objects.get(owner=transaction.recipient)
        amount = transaction.amount

        transaction_date = str(transaction.datetime_transfer).split(" ")[0]
        if transaction_date == date:
            sender_account.amount -= amount
            recipient_account.amount += amount
            sender_account.save()
            recipient_account.save()

#------------------------------------------------#


# Create your views here.
class ListUsersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        #user = Users.objects.all()
        """
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)
        """

        #queryset = get_object_or_404(Users, email=request.user)
        queryset = user
        serializer = ListUserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
        #return Response({"response": str(request.META['REMOTE_ADDR'])})
        #return Response({"response": str(request.headers.get('User-Agent'))})

class SignupUserView(APIView):

    def post(self, request, *args, **kargs):

        # Le domaine 
        #domain = "http://localhost:8000/api/v1/"
        domain = "http://devinstapay.pythonanywhere.com/api/v1/"
        
        # On récupération des informations 
        full_name = request.data['full_name']
        email_user = request.data['email']
        password_user = request.data['password']
        code_temp = CodeGenerator() # Génération du code de confirmation du compte 

        # Vérifions que l'email n'existe pas encore et que le champs nom à bien été remplit
        
        if Users.objects.filter(email=email_user).exists():
            obj = {"erreur": "Cette adresse mail est déjà utilisé"}
            return Response(obj, status=status.HTTP_406_NOT_ACCEPTABLE) #406 pas acceptable
        elif full_name == "" or full_name == None:
            obj = {"erreur": "Le champs Nom ne peut pas être vide !"}
            return Response(obj, status=status.HTTP_406_NOT_ACCEPTABLE) #406 pas acceptable


        # Création du compte utilisateur
        Users.objects.create_user(
            email=email_user, 
            password=password_user
        )

        user = get_object_or_404(Users, email=email_user)
        user.full_name = full_name
        user.code_temp = code_temp
        user.save()

        # Envoie du Mail de confirmation
        receiver = email_user
        subject = "Activation du compte"
        body = f"""
Hello {full_name},
Le Code De Confirmation Est Le Suivant : {code_temp}.

Vous Pouvez Aussi Cliquez Sur Le Lien Suivant Pour Activer Votre Compte
LE LIEN DE CONFIRMATION DE CONFIRMATION : {domain}active_my_account/{code_temp}/

Attention Ce Code N'est Valide Que Pendant 5 Min !
"""
        email_thread = threading.Thread(target=SendMail, args=(receiver, subject, body))
        email_thread.start()

        # Décompte pour le code confirmation
        #th1 = threading.Thread(Countdown, args=(email_user))
        #th1.start()
        
        # LA REPONSE
        obj = {
            "result": f"Le Code de confirmation à été envoyé à {email_user}"
        }
        return Response(obj, status=status.HTTP_201_CREATED)


# ACTIVATION DU COMPTE DE l'UTILISATEUR
class ActivateUserAccountView(APIView):

    def get(self, request, *args, **kargs):

        # On récupère le code d'activation du code 
        path = str(request.path_info)
        path = path.split("/")
        code = path[len(path)-2]
        
        user = get_object_or_404(Users, code_temp=code)
        user.code_temp = "111111"
        user.save()

        # Création du compte Instapay de l'utilisateur 
        provider = get_object_or_404(Providers, name="Instapay")
        account = UserAccounts.objects.create(owner=user, provider=provider)

        body = "<h1 style='color: green'>INSTAPAY</h1><p>Votre compte est maintenant activé</p>"
        return HttpResponse(body)

# CONNEXION AU COMPTE UTILISATEUR
class SendCodeToResetPasswordView(APIView):

    def post(self, request, *args, **kargs):

        # Vérifions que l'utilisateur existe déja dans notre base de données
        user = get_object_or_404(Users, email=request.data['email'])
        # Vérifions également qu'il possède bien un compte 
        account = get_object_or_404(UserAccounts, owner=user)

        # Récupèration des données 
        # On va envoyé un mail à l'utilisateur contenant son nouveau mot de passe
        email_receiver = user.email
        subject = "Restauration Mot De Passe !"
        code_temp = CodeGenerator(size=10, numeric=0)
        body = f"""
Hello,

Connectez Vous Avec Ce Nouveau Code Puis Changer Le Une fois Connecté
Mot De Passe : {code_temp}

Attention Ce Code N'est Valide Que Pendant 5 Min !
"""
        reset_mdp_thread = threading.Thread(target=SendMail, args=(email_receiver, subject, body))
        reset_mdp_thread.start()

        # Mise à jour code de confirmation 
        user = get_object_or_404(Users, email=request.data['email'])
        user.code_temp = code_temp
        user.save()

        # On lance le décompte pour reset le code de confirmation 
        #reset_confirmation_code_thread = threading.Thread(target=Countdown, args=(Users, user.email,"reset_password"))
        #reset_confirmation_code_thread.start()

        # La reponse 
        obj = {
            "success": "Consulter votre boîte mail !"
        }
        return Response(obj, status=status.HTTP_200_OK) #200

class ResetPasswordUserView(APIView):
    
    def post(self, request, *args, **kargs):
        
        # Récupération des données (Code envoyés par mail, Nouveau Mot De Passe)
        try:
            email = request.data['email']
            code = request.data['reset_code']
            new_password = request.data['new_password']
        except:
            obj = {"errors": "L'une des clé n'est pas correcte"}
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)

        # Vérifions que l'utilisateur existe déja dans notre base de données
        user = get_object_or_404(Users, email=email)
        # Vérifions également qu'il possède bien un compte 
        account = get_object_or_404(UserAccounts, owner=user)

        # Vérification et Application des modifications
        if code == user.code_temp:
            user.set_password(new_password)
            user.double_authentication = 0
            user.double_authentication_code = None
            account.account_protection = 0
            account.protection_code = 0
            user.save()
            account.save()

            obj = {
                "success": "Password Reset !"
            }
            return Response(obj, status=status.HTTP_200_OK)
        else:
            obj = {
                "error": "Impossible to reset user password !"
            }
            return Response(obj, status=status.HTTP_406_NOT_ACCEPTABLE) #406

class ChangePasswordUserView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)

        # Récupération des informations 
        old_password = request.data['old_password']
        new_password = request.data['new_password']

        # Changement du mot de passe de l'utilisateur 
        queryset = get_object_or_404(Users, email=request.user)
        queryset.set_password(new_password)

        # La reponse 
        obj = {
            "success": "Mot de passe changé"
        }
        return Response(obj, status=status.HTTP_200_OK) #200

class LoginForSecondAuthentication(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kargs):
        
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            code = CodeGenerator(size=8)
            receiver = user.email
            subject = "Double Authentification"
            body = f"""
Le Code Pour La Seconde Authentification Est : {code} 
"""
            user.double_authentication_code = HashSecondAuthenticationCode(code)
            user.save()
            th1 = threading.Thread(target=SendMail, args=(receiver, subject, body))
            th1.start()

            obj = {"success": True}
            return Response(obj, status=status.HTTP_200_OK)
        else:
            obj = {"success": False}

    def post(self, request, *args, **kargs):
        
        # Récupèration du code pour la double authentification et le user
        user = get_object_or_404(Users, email=request.user)
        try:
            code = request.data['second_authentication_code']
        except:
            return Response({"errors": "La clé est incorrete"}, status=status.HTTP_400_BAD_REQUEST)
        code = HashSecondAuthenticationCode(code)

        if user.double_authentication == 1 and user.double_authentication_code == code:
            user.double_authentication_validated = 1
            user.save()

        obj = {"success": "Double authentification réussie"}
        return Response(obj, status=status.HTTP_200_OK)

# ------------ DECONNECION -------------
class LogoutUserView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)

        """
        serializer = LogoutSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        """

        try:
            refresh_token = request.data['refresh']
        except:
            obj = {"errors": "Token de rafraichissement requis !"}

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            raise ValueError("Token already expired !")
        logout(request)

        if user.double_authentication:
            user.double_authentication_validated = 0
            user.double_authentication_code = HashSecondAuthenticationCode("empty")
            user.last_login = datetime.today()
            user.save()

        obj = {"response": "User logout"}
        return Response(obj, status=status.HTTP_200_OK)

# ------------- USER PROFILES ----------------
class EditUserProfilView(APIView):

    def put(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            full_name = self.request.data["full_name"]
            email = self.request.data['email_user']
            phone_number = self.request.data['phone_number']
        except:
            obj = {"errors": "full_name, email_user, phone_number sont requis"}
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(Users, email=request.user)

        if full_name:
            user.full_name = full_name
        
        if email:
            user.email = email
        
        if phone_number:
            user.phone_number = phone_number

        user.save()
        obj = {"succès": "Mise à jour réussie"}
        return Response(obj, status=status.HTTP_200_OK)


# -------------- SECURITE ---------------------
class SecurityUserView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)

        obj = {"resposne": ""}

        # On récupère les informations présente dans la requête puis on met à jour les donénes
        if self.request.GET.get('double_authentication'):
            double_authentication = self.request.GET.get('double_authentication')
            if int(double_authentication) == 1 or int(double_authentication) == 0:
                #return Response(obj, status=status.HTTP_200_OK)
                user.double_authentication = int(double_authentication)
                user.save()
                obj["double_authentication"] = "Activate"
        
        if self.request.GET.get('email_alert'):
            email_alert = int(self.request.GET.get('email_alert'))
            if email_alert == 1 or email_alert == 0:
                user.alert_mail = 1
                user.save()
                obj["alert_mail"] = "Activate"

        if self.request.GET.get('account_protection'):
            account_protection = int(self.request.GET.get('account_protection'))
            
            try:
                account_protection_code = self.request.data['account_protection_code']
                account_user = get_object_or_404(UserAccounts, owner=user)
            except:
                obj = {"errors": "Code de protection requis !"}
                return Response(obj, status=status.HTTP_400_BAD_REQUEST)

            if account_protection:

                account_protection_code_hash = HashSecondAuthenticationCode(account_protection_code)
                account_user.account_protection = 1
                account_user.protection_code = account_protection_code_hash
                account_user.save()
                obj["account_protection_activation"] = "Activé"
            else:
                if account_user.account_protection: # Si la protection du compte est activé alors on demande le code pin
                    # Avant de le désactiver
                    account_protection_code_hash = HashSecondAuthenticationCode(account_protection_code)
                    if account_protection_code_hash == account_user.protection_code:
                        account_user.account_protection = 0
                        account_user.protection_code = None
                        account_user.save()
                        obj["account_protection_deactivation"] = "Désactivé" #Désactiver avec succès
                    else:
                        obj["account_protection_deactivation"] = "Impossible de désactivé l'option, Code de protection incorrecte"
                else:
                    return Response({"problem detected": "Okay C'est bon !"})
            
        return Response(obj, status=status.HTTP_200_OK)
                

# -------------- TRANSACTIONS ---------------------
class UserTransactionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)
        
        # On affiche la liste des transactions de l'utilisateur
        
        queryset_sender = Transactions.objects.filter(sender=user)
        queryset_recipient = Transactions.objects.filter(recipient=user)
        serializer_sender = UserTransactionSerializer(queryset_sender, many=True)
        serializer_recipient = UserTransactionSerializer(queryset_recipient, many=True)
        serializer = {
            "sender": serializer_sender.data,
            "recipient": serializer_recipient.data
        }
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)

        # Réucupération des informations
        sender = get_object_or_404(Users, email=request.user)
        sender_account = get_object_or_404(UserAccounts, owner=sender)
        recipient = get_object_or_404(Users, email=request.data['receiver'])
        recipient_account = get_object_or_404(UserAccounts, owner=recipient)
        amount = float(request.data['amount'])

        # Vérification avant transaction
        dotransaction = 0

        if sender_account.account_protection:
            try:
                protection_code = request.data['account_protection_code']
                protection_code_hash = HashSecondAuthenticationCode(protection_code)
                if protection_code_hash == sender_account.protection_code:
                    dotransaction = 1
                else:
                    obj = {"erreur": "Opération non authorisé"}
                    return Response(obj, status=status.HTTP_401_UNAUTHORIZED)
            except:
                obj = {"erreur": "Mauvaise requête"}
                return Response(obj, status=status.HTTP_400_BAD_REQUEST)
        else:
            dotransaction = 1

        if sender.email == recipient.email:
            obj = {"erreur": "Vous ne pouvez pas vous envoyez de l'argent"}
            return Response(obj, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not request.data['date']:
            obj = {"erreur": "La clé 'date' est requise "}
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)
        
        # On éffectue la transaction 
        if sender_account.amount > amount and dotransaction == 1:

            today = str(datetime.today())
            today = today.split(" ")[0]
            date = str(request.data["date"])
            if  date == today:
                sender_account.amount -= amount
                recipient_account.amount += amount
                sender_account.save()
                recipient_account.save()
                obj = {"succès": "Transaction réussie"}
                state = 1
            else:
                obj = {"succès": "Transaction enrégistrée"}
                state = 0

            Transactions.objects.create(amount=amount, sender=sender, recipient=recipient, status=1, state=state, datetime_transfer=date)

            return Response(obj, status=status.HTTP_200_OK)
        else:
            obj = {"erreur": "Solde insuffisant pour éffectuer la transaction"}
            return Response(obj, status=status.HTTP_406_NOT_ACCEPTABLE)

class PaymentRequest(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)

        # Récupèration des données 
        sender = get_object_or_404(Users, email=request.user)
        recipient = get_object_or_404(Users, email=request.data['receiver'])
        full_name_sender = sender.full_name
        full_name_receiver = recipient.full_name
        amount = request.data['amount']
        reason = request.data['reason']

        receiver = recipient.email
        subject = "Requête de Paiement"
        body = f"""
Hello , {full_name_receiver}
Requête de Paiement Venant De : M(me) {full_name_sender}
Montant                       : {amount}
Motif                         : {reason}
"""
        email_thread = threading.Thread(target=SendMail, args=(receiver, subject, body))
        email_thread.start()

        obj = {"succès": "Requête de paiement envoyé"}
        return Response(obj, status=status.HTTP_200_OK)

class UserAccountView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kargs):

        # Vérification pour les users avec double authentification 
        user = get_object_or_404(Users, email=request.user)
        if user.double_authentication:
            if not user.double_authentication_validated:
                obj = {"erreur": "Accès non autorisé"}
                return Response(obj, status=status.HTTP_401_UNAUTHORIZED)

        queryset = get_object_or_404(UserAccounts, owner=request.user.id)
        serializer = UserAccountSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

"""
{
"full_name": "Nade Fabrice",
"email": "nadefabrice83@gmail.com",
"password": "password"
}
"""