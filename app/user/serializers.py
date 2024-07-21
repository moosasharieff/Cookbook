"""
Serializer for the user API View.
"""
from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers

from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        """Defining the params to include in db and validation
        conditions to be applied for user provided data."""
        # Define db model to store data
        model = get_user_model()
        # Expected user data in payload
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        """Create and return user object with encrypted data."""
        return get_user_model().objects.create_user(**validated_data)

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user auth token"""
    # Fields required for serializing auth token for user
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user data."""
        email = attrs.get('email')
        password = attrs.get('password')
        # Authenticate user
        # Overriding `username` with `email`
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        # If user is not found in db, raise error
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code='authorization')

        # Adding 'user' object to the var: attrs
        attrs['user'] = user
        return attrs

