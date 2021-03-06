from django.contrib.auth import get_user_model, authenticate
# from django.utils.translation import ugettext_lazy as _  # automatically
# convert to correct language

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer the user object
    """

    class Meta:
        model = get_user_model()
        # Field you want to include
        fields = ('email', 'password', 'name')
        # Ensure password is more than 5 characters, and write only
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user, setting the password correctly and return it
        """
        # First, we remove the password from validated_data
        password = validated_data.pop('password', None)
        # Run update user and set password
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializser for the user authentication object
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # Our validation, check input are correct
    def validate(self, attrs):
        """
        Validate and authenticate the user
        """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            # 1st argument => request you want to authenticate
            request=self.context.get('request'),
            username=email,
            password=password
        )
        # Authentication fail
        if not user:
            msg = ('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
