from django import forms

class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=50, required=True)
    firstName = forms.CharField(label='Imię', max_length=25, required=True)
    indexNumber = forms.CharField(label='Numer albumu', max_length=25, required=True)
    password = forms.CharField(label='Hasło', min_length=5, max_length=50, required=True, widget=forms.widgets.PasswordInput)
    confirmPassword = forms.CharField(label='Powtórz Hasło', min_length=5, max_length=50, required=True, widget=forms.widgets.PasswordInput)

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=50, required=True)
    password = forms.CharField(label='Hasło', min_length=5, max_length=50, required=True, widget=forms.widgets.PasswordInput)

class AddCourseForm(forms.Form):
    title = forms.CharField(label='Przedmiot', max_length=50, required=True)
    description = forms.CharField(label='Opis', max_length=200, required=False, widget=forms.widgets.Textarea)

class AddExamForm(forms.Form):
    description = forms.CharField(label='Nazwa egzaminu', max_length=80, required=True, widget=forms.widgets.Textarea)
    screenshotFile = forms.ImageField(label='Screen programu', required=False)