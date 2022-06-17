from tabnanny import verbose
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Series(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Series title"))
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "series"

    def __str__(self) -> str:
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="courses_created",
        verbose_name=_("Course creator"),
        null=True,
    )
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("series"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Course title"))
    slug = models.SlugField(max_length=200)
    overview = models.TextField()
    hero_image = models.ImageField(
        verbose_name=_("Course image"), 
        upload_to="courses", 
        blank=True
    )
    released_date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-released_date"]


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="modules",
        verbose_name=_("Module"),
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200, verbose_name=_("Module title"))
    description = models.TextField(verbose_name=_("Description"), blank=True)

    def __str__(self) -> str:
        return self.title
