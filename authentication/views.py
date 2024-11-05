from django.shortcuts import render
from django.db import IntegrityError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

import datetime

from authentication.models import User


class LoginView(TokenObtainPairView):
    def finalize_response(self, request, response: Response, *args, **kwargs):

        if response.status_code == 200:
            refresh_token = response.data["refresh"]
            access_token = response.data["access"]
            response = Response({
                "ok": True,
                "token": access_token,
                "role": RefreshToken(refresh_token).get('role')
            })
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                # secure=True,
                path="/auth/refresh",
                # samesite="None",
                expires=datetime.timedelta(days=15),
                max_age=3000
            )
        return super().finalize_response(request, response, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        if refresh_token := response.data.get('refresh'):
            response.set_cookie(
                'refresh_token',
                str(refresh_token),
                httponly=True,
                samesite="None",
                secure=True,
                path="/auth/refresh",
                expires=datetime.timedelta(days=15),
                max_age=3000
            )

            access = response.data['access']

            del response.data['refresh']
            del response.data['access']

            response.data['ok'] = True
            response.data['token'] = access

            return super().finalize_response(request, response, *args, **kwargs)

        return super().finalize_response(response, Response({"ok": False}, status=401), *args, **kwargs)


@api_view(['POST'])
def register(request: Request):
    if User.objects.filter(username=request.data['username']).exists():
        return Response({"ok": False, "error": "Username already registered!"})
    if User.objects.filter(email_id=request.data['email_id']).exists():
        return Response({"ok": False, "error": "Emailid already registered!"})
    if request.data['password'] != request.data['re_password']:
        return Response({"ok": False, "error": "Passwords don't match!"})

    try:
        User.objects.create_user(
            username=request.data['username'],
            email_id=request.data['email_id'],
            password=request.data['password']
        )

    except IntegrityError as e:
        print("error", e)
        return Response({"ok": False, "error": "User already registered!"})

    return Response({"ok": True})
