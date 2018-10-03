
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class MyUserManager(BaseUserManager):
  """
  A custom user manager to deal with emails as unique identifiers for auth
  instead of usernames. The default that's used is "UserManager"
  """
  def _create_user(self, username, password, **extra_fields):
    """
    Creates and saves a User with the given username and password.
    """
    if not username:
      raise ValueError('The username must be set')
    # username = self.normalize_username(username)
    user = self.model(username=username, **extra_fields)
    user.set_password(password)
    # user.EmailField(email)
    user.save()
    return user

  def create_superuser(self, username, password, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_active', True)
    extra_fields.setdefault('verified', True)
    extra_fields.setdefault('email', 'admin@admin.com')
    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')
    return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
  
  is_staff = models.BooleanField(
    'staff status',
    default=False,
    help_text=('Designates whether the user can log into this site.'),
  )
  is_active = models.BooleanField(
    'active',
    default=True,
    help_text=(
      'Designates whether this user should be treated as active. '
      'Unselect this instead of deleting accounts.'
    ),
  )
  
  email = models.EmailField(unique=True, null=True)
  is_superuser = models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')
  username     = models.CharField(unique=True, max_length=64, verbose_name='Username')
  verified     = models.BooleanField(default=False)
  created_at   = models.DateTimeField(auto_now_add=True)
  updated_at   = models.DateTimeField(auto_now=True)
  wallet_address = models.CharField(null=True, unique=True, max_length=64, verbose_name='Wallet Address')
  signature = models.CharField(null=True, unique=True, max_length=128, verbose_name='Signature')
  message = models.CharField(null=True, unique=True, max_length=128, verbose_name='Message')
  final_message = models.CharField(null=True, unique=True, max_length=128, verbose_name='Message')


  USERNAME_FIELD = 'username'
  objects = MyUserManager()


  def __str__(self):
    return self.username


  def get_short_name(self):
    return self.username
    
  # @property
  # def id_back_url(self):
  #     if self.id_back and hasattr(self.id_back, 'url'):
  #         return self.id_back.url
  #     else:
  #         return '/static/images/placeholder.png'
