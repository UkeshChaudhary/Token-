from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .emails import *


# Create your views here.


# Register API

class RegisterAPI(APIView):
     
    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                send_otp_via_email(serializer.data['email'])
                return Response({
                        'message' : 'Registration is Sucessfully done.',
                        'data' : serializer.data,
                }, status=status.HTTP_200_OK)
            return Response({
                'message' : 'Something went wrong',
                'data' : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)



# Verify Email

class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data=data)


            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']

                user = User.objects.filter(email = email)
                if not user.exists():
                    return Response({
                        'message' : 'Something went wrong',
                        'data' : 'invalid email'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not user[0].otp == otp:
                    return Response({
                        'message' : 'Something went wrong',
                        'data' : 'wrong otp'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user = user.first()
                user.is_verified = True
                user.save()

                return Response({
                    'message' : 'account Verified',
                    'data' : {}
                }, status=status.HTTP_201_CREATED) 

            return Response({
                'message' : 'Something went wrong',
                'data' : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)  

                
        except Exception as e:
            print(e)


# Login View
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
import jwt, datetime

class LoginView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            
               
            if user is not None:
                if user.is_verified:
                    playload ={
                        'id':user.id,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                        'iat': datetime.datetime.utcnow()
                    }  

                    token = jwt.encode(playload, 'secret', algorithm='HS256')
                    
                    response = Response()

                    response.set_cookie(key='jwt', value=token, httponly=True)

                    response.data = {
                        'jwt': token
                    }

                    return response
                return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
            
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.exceptions import AuthenticationFailed
class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticate!')
        
        try:
            playload = jwt.decode(token, 'secret', algorithms=['HS256'])
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.get(id = playload['id'])
        serializer = UserSerializer(user)


        return Response(serializer.data)
    

class LogoutView(APIView):
    
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'User Sucessfully Deleted!'
        }

        return response