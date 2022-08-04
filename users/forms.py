from allauth.account.forms import SignupForm
from django import forms as d_forms
from django.contrib.auth import forms, get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = d_forms.EmailField(required=True, help_text="Required")

    error_message = UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_email(self):
        """
        Verify email is available.
        """
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError(
                "Email is either invalid or already taken"
            )
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise ValidationError(self.error_messages["duplicate_username"])


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["name"].required = True


#  Django allauth authentication
class AcademySignUpForm(SignupForm):
    # specify a choice field that matches choice fields on our model

    type = d_forms.ChoiceField(
        choices=[("STUDENT", "Student"), ("INSTRUCTOR", "Instructor")]
    )

    def custom_signup(self, request, user):
        # set the user type from the form response

        user.type = self.cleaned_data["type"]
        user_group = Group.objects.get(name="Instructor")
        if user.type == User.Types.INSTRUCTOR:
            user_group.user_set.add(user)
        user.save()
