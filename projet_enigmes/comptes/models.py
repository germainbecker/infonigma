from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.crypto import get_random_string

class EnseignantManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Les enseignants doivent avoir une adresse email')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = False  # L'utilisateur est inactif jusqu'à la confirmation de l'email
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

class Enseignant(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    accepte_cgu = models.BooleanField(default=False, verbose_name="Accepte les CGU")

    email_confirmation_token = models.CharField(max_length=100, blank=True)

    objects = EnseignantManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def generate_email_confirmation_token(self):
        self.email_confirmation_token = get_random_string(64)
        self.save()
