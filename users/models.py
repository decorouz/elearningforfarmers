from typing import List

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: List[str] = []

    objects = UserManager()

    class Types(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"

    base_type = Types.INSTRUCTOR

    # what type of use are we?
    type = models.CharField(
        _("Type"), choices=Types.choices, default=base_type, max_length=50
    )

    # First name and last name do not cover name patterns around the world
    name = models.CharField(_("Name of user"), max_length=255, blank=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.email})

    def save(self, *args, **kwargs):
        if not self.id:
            self.type = self.base_type
        return super().save(*args, **kwargs)


class StudentManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(type=User.Types.STUDENT)
        )


class Student(User):
    base_type = User.Types.STUDENT

    objects = StudentManager()

    class Meta:
        proxy = True


class InstructorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(type=User.Types.INSTRUCTOR)
        )


class Instructor(User):
    base_type = User.Types.INSTRUCTOR

    objects = InstructorManager()

    class Meta:
        proxy = True
