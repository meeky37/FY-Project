from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
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
        return Response({'success': True, 'access_token': str(refresh.access_token), 'refresh_token': str(refresh)})
    else:
        return Response({'success': False, 'error': 'Invalid credentials'})
