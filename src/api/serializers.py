from rest_framework.serializers import ModelSerializer, Serializer

#from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from api.models import Transactions, Users, UserAccounts

class ListUserSerializer(ModelSerializer):

    class Meta:
        model = Users 
        fields = ["full_name", "email", "phone_number", "status", "double_authentication"]

class SigninuserSerializer(ModelSerializer):

    class Meta:
        model = Users 
        fields = '__all__'

class UserAccountSerializer(ModelSerializer):

    class Meta:
        model = UserAccounts
        exclude = ["protection_code", "id", "owner"]

class UserTransactionSerializer(ModelSerializer):

    class Meta:
        model = Transactions
        fields = '__all__'

"""
class LogoutSerializer(Serializer):

    refresh = Serializer.Charfield()

    def validate(self, data):
        self.token = data['refresh']
        return data

    # Nous rendons ce token là invalid à présent
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad token')
"""
