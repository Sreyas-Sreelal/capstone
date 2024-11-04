from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request

class CustomTokenAuthentication(JWTAuthentication):
    def get_header(self, request: Request) -> bytes:
        return request.META.get("HTTP_TOKEN")

    def get_raw_token(self, header):
        return header
