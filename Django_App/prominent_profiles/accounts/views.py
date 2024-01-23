from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from .models import Subscription
from .serializers import CustomUserSerializer

from profiles_app.models import Entity


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registers a user provided they email is unique"""
    # TODO: Extend to phone number?
    data = request.data

    serializer = CustomUserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        print(f"User created successfully: {user.email}")
        return Response({'success': True, 'message': 'User sign-up success!'})
    else:
        print(f"User sign-up failed: {serializer.errors}")

        if 'email' in serializer.errors and 'unique' in serializer.errors['email'][0].code:
            return Response(
                {'success': False, 'errors': {'email': 'This email is already registered.'}},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    """Handles a login case of email or phone number.
       The '@' should be suitable as validation in VueJS covers this holistically beforehand"""

    input_data = request.data
    user_input = input_data.get('input')
    password = input_data.get('password')

    is_email = '@' in user_input
    if is_email:
        user = authenticate(request, email=user_input, password=password)
    else:
        user = authenticate(request, phone_number=user_input, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            {'success': True, 'access_token': access_token, 'refresh_token': refresh_token})
    else:
        return Response({'success': False, 'error': 'Invalid credentials'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_user_data(request):
    """Obtains info for personal dashboard welcome"""
    user = request.user
    print(user)
    user_data = {
        'first_name': user.first_name,
        # 'last_name': user.last_name,
    }
    return Response(user_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def toggle_sub(request, entity_id):
    """Processes a users request to (un-)subscribe"""
    user = request.user
    print(user)

    entity = get_object_or_404(Entity, id=entity_id)

    try:
        # Check for sub and delete if exists (toggle off)
        subscription = Subscription.objects.get(user=user, entity=entity)
        subscription.delete()
        status = 'removed'
    except Subscription.DoesNotExist:
        # Create a new subscription (toggle on)
        Subscription.objects.create(user=user, entity=entity)
        status = 'added'

    return JsonResponse({'status': status})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_sub_status(request, entity_id):
    """Identifies if a user is subscribed to the entity they are viewing in frontend"""
    sub = Subscription.objects.filter(user=request.user, entity=entity_id).first()
    status = True if sub else False
    return JsonResponse({'status': status})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_sub_list(request):
    """Gets a list of every entity a user is subscribed to for the dashboard page"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'})

    subscribed_entities = Subscription.objects.filter(user=request.user).values('entity')
    entity_ids = [entry['entity'] for entry in subscribed_entities]
    entities_data = Entity.objects.filter(id__in=entity_ids).values('id', 'name')
    entities_list = list(entities_data)

    return JsonResponse({'subscribed_entities': entities_list})
