from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

# Create your models here.
class MyUserManager(BaseUserManager):

    def create_user(self, email, password):
        if not email or not password:
            raise ValueError("Email, Password are required !")

        user = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.is_stuff = True 
        user.save()
        return user

class Users(AbstractBaseUser):
    
    email = models.EmailField(unique=True, max_length=255, blank=False)
    full_name = models.CharField(max_length=100, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=100, default="client")
    code_temp = models.CharField(max_length=6)
    double_authentication = models.BooleanField(default=False)
    double_authentication_code = models.CharField(max_length=6, blank=True, null=True)
    double_authentication_validated = models.BooleanField(default=False)
    alert_mail = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # Les informations personnelle

    USERNAME_FIELD = "email"
    objects = MyUserManager()

    def has_perm(self, perm, obj=None):
        return True 

    def has_module_perms(self, app_label):
        return True

class Providers(models.Model):

    name = models.CharField(max_length=100, default="Instapay", unique=True, null=False, blank=False)
    date_added = models.DateTimeField(auto_now_add=True)
    state = models.BooleanField(default=False)


# LA TABLE DES COMPTES
class UserAccounts(models.Model):

    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="owner")
    provider = models.ForeignKey(Providers, on_delete=models.CASCADE, related_name="provider")
    status = models.BooleanField(default=True)
    amount = models.FloatField(default=1000000)
    date_created = models.DateTimeField(auto_now_add=True)
    account_protection = models.BooleanField(default=False)
    protection_code = models.CharField(max_length=100, blank=True, null=True)

# LA TABLE DES TRANSACTIONS
class Transactions(models.Model):
    
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="recipient")
    amount = models.FloatField()
    datetime_transfer = models.DateTimeField()
    status = models.BooleanField(default=True)
    state = models.CharField(max_length=100, blank=False, null=False, default="done")
    #show = models.BooleanField(default=True)

# LES LOGS DU SYSTEME
class MyLogs(models.Model):

    log_type = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="users_logs")
    datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=100, blank=False, null=False)
    status = models.BooleanField(default=False)
    device_user = models.CharField(max_length=100)

# LA TABLES QUI STOCKE LES PERIMETRES ET LA LOCALISATION DES UTILISATEURS
class UserInfos(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="users_info")
    device = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)
    location = models.CharField(max_length=100)