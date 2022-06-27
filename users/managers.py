from time import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def _create(self, email, password, is_staff, is_superuser, **extrafields):
        if not email:
            raise ValueError("Users must have an email address")

        now = timezone.now
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extrafields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extrafields):
        print(**extrafields)
        return self._create(email, password, False, False, **extrafields)

    def create_superuser(self, email, password, **extrafields):
        user = self._create(email, password, True, True, **extrafields)
        return user
