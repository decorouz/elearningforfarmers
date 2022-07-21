from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .fields import OrderField

# User = get_user_model()


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
        related_name="course_creator",
        verbose_name=_("Course creator"),
        null=True,
    )
    students = models.ManyToManyField(
        User, related_name="courses_joined", blank=True
    )
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("course series"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Course title"))
    slug = models.SlugField(max_length=200, blank=True)
    overview = models.TextField()
    hero_image = models.ImageField(
        verbose_name=_("Course image"),
        upload_to="courses",
        null=True,
        blank=True,
    )
    released_date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-released_date"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Course, self).save(*args, **kwargs)


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="modules",
        verbose_name=_("course module"),
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200, verbose_name=_("Module title"))
    order = OrderField(blank=True, for_fields=["course"])
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        unique_together = ("course", "order")
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.order}. {self.title}"


class Content(models.Model):
    "Add different type of content to course modules"
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "video", "image", "file")},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    order = OrderField(blank=True, for_fields=["module"])

    class Meta:
        ordering = ["order"]


class ItemBase(models.Model):
    creator = models.ForeignKey(
        User, related_name="%(class)s_related", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

    def render(self):
        return render_to_string(
            f"courses/content/{self._meta.model_name}.html", {"item": self}
        )


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to="files")


class Image(ItemBase):
    module_image = models.ImageField(upload_to="images")


class Video(ItemBase):
    video_url = models.URLField()


# class Question(models.Model):
#     course = models.ForeignKey(
#         Course,
#         related_name="questions",
#         on_delete=models.CASCADE,
#         verbose_name=_("questions"),
#     )
#     text = models.CharField(
#         max_length=1000, verbose_name=_("text"), null=True, blank=True
#     )

#     def __str__(self) -> str:
#         return self.text


# class Answer(models.Model):
#     question = models.ForeignKey(
#         Question, related_name="correct_answer", on_delete=models.CASCADE
#     )
#     text = models.CharField(max_length=1000, verbose_name=_("text"))
#     correct_answer = models.BooleanField(blank=True)

#     def __str__(self) -> str:
#         return self.text


# class UserResponse(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="user",
#         verbose_name=_("users"),
#     )
#     question = models.ForeignKey(
#         Question,
#         related_name="question",
#         verbose_name=_("user response"),
#         on_delete=models.CASCADE,
#     )
#     response = models.ForeignKey(
#         Answer,
#         on_delete=models.DO_NOTHING,
#         related_name="response_answer",
#         verbose_name=_("user answer"),
#     )

#     class Meta:
#         # ensures that a user provides an answer per question
#         unique_together = ("question", "user")
