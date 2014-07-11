from django import forms
from . import models      

class BathroomForm(forms.ModelForm):
    class Meta:
        model = models.Bathroom
        fields = ['name', 'description', 'createdBy']