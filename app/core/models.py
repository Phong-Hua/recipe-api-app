from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


# Create user manager class
class UserManager(BaseUserManager):
    # **extra_fields, take any extra argument pass in when
    # call this function as extra field
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user
        """
        if not email:
            raise ValueError('Users must have an email address')
        # we normalized email as email is case senstive
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # password need to be encrypted
        user.set_password(password)
        # using=self.db this bit is required for multiple databases
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user


# Create custom user model
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)

    name = models.CharField(max_length=255)     # CharField is character field

    is_active = models.BooleanField(default=True)   # this user is active

    is_staff = models.BooleanField(default=False)   # this user is not staff

    objects = UserManager()

    USERNAME_FIELD = 'email'

    # Next, we add custom user model to settings.py and do migrations
