from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter student name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A student with this email already exists.")
        return email

