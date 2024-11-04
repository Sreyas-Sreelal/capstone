from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

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