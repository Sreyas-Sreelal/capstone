from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework import serializers

from . import models

class CustomTokenObtainPairSerliazer(TokenObtainPairSerializer):
    def get_token(self,user):
        token = super().get_token(user)
        token.payload['role'] = user.role
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None
    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken("No refresh token found in cookie")
    
    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)

class CertificationsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Certifications
    
class UserSerializer(serializers.ModelSerializer):
    certifications = CertificationsSerializer(read_only=True,many=True)
    class Meta:
        fields = "__all__"
        model = models.User
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('include', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for x in existing - allowed:
                self.fields.pop(x)
