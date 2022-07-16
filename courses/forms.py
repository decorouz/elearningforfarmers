from django import forms
from django.forms.models import inlineformset_factory

from .models import Course, Module

# Since Course is divided into a variable number of
# modules, it make sense to use formsets to manag them

# Allow user to create multiple modules at once.

ModuleInlineFormSet = inlineformset_factory(
    Course, Module, fields=["title", "description"], extra=2, can_delete=True
)
