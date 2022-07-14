from django.core.exceptions import ValidationError
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# User = get_user_model()


# class UserSignUpForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ("email", "password1", "password2")

#     def save(self, commit=True):
#         user = super(UserSignUpForm, self).save(commit=False)
#         user.email = self.cleaned_data["email"]
#         if commit:
#             user.save()
#         return user

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         if User.objects.filter(email=email).exists():
#             raise ValidationError("A user with this email already exist")
#         return email
