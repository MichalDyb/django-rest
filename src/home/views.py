from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View 
import requests
from requests.sessions import session
from requests_toolbelt import MultipartEncoder, multipart
from .forms import *
from django.urls import reverse

# Klasa widoku strony głównej
class IndexView(View):
    template_name = 'home/index.html' 
    title = 'Strona główna'                          
    context = {'title': title}
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

class RegisterView(View):
    template_name = 'home/register.html' 
    title = 'Rejestracja'
    form = RegisterForm()                     
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Auth/Register'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' in request.session:
            return render(request, 'home/index.html', {'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze wylogować!'})
        return render(request, self.template_name, {'title': self.title, 'form': self.form})

    def post(self, request, *args, **kwargs):
        if 'user' in request.session:
            return render(request, 'home/index.html', {'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze wylogować!'})
        self.form = RegisterForm(request.POST)
        if self.form.is_valid():
            data = self.form.cleaned_data
            response = requests.post(self.url, json=data, headers={'Content-Type': 'application/json'})
            message = response.json()['message']
            if response.status_code == 200:
                self.form = RegisterForm()
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'info': message})
            elif response.status_code == 400:
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'error': message})
        return render(request, self.template_name, {'title': self.title, 'form': self.form})

class LoginView(View):
    template_name = 'home/login.html' 
    title = 'Logowanie'        
    form = LoginForm()                    
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Auth/Login'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' in request.session:
            return render(request, 'home/index.html', {'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze wylogować!'})
        return render(request, self.template_name, {'title': self.title, 'form': self.form})

    def post(self, request, *args, **kwargs):
        if 'user' in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze wylogować!'})
        self.form = LoginForm(request.POST)
        if self.form.is_valid():
            data = self.form.cleaned_data
            response = requests.post(self.url, json=data, headers={'Content-Type': 'application/json'})
            message = response.json()['message']
            if response.status_code == 200:
                request.session['user'] = {
                    'email': response.json()['userInfo']['Email'],
                    'id': response.json()['userInfo']['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'],
                    'token': response.json()['message']
                }
                return render(request, 'home/index.html', {'title': self.title, 'main_info': 'Zostałeś zalogowany poprawnie :)'})
            elif response.status_code == 400:
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'error': message})
        return render(request, self.template_name, {'title': self.title, 'form': self.form})

class LogoutView(View):
    template_name = 'home/login.html' 
    title = 'Logowanie'        
    form = LoginForm()                    
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Auth/Login'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})
        else:
            request.session.flush()
            return render(request, 'home/index.html', {'title': self.title, 'main_info': 'Zostałeś wylogowany poprawnie :)'})

class AddCourseView(View):
    template_name = 'home/add_course.html' 
    title = 'Dodaj przedmiot'        
    form = AddCourseForm()                 
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Course'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})
        return render(request, self.template_name, {'title': self.title, 'form': self.form})

    def post(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})
        self.form = AddCourseForm(request.POST)
        if self.form.is_valid():
            data = self.form.cleaned_data           

            session = requests.Session()
            session.headers.update({
            'Authorization': 'Bearer '+ request.session['user']['token']
            })
            response = session.post(self.url, data=data, headers={})

            if response.status_code == 200:
                return render(request, self.template_name, {'title': self.title, 'form': AddCourseForm(), 'info': 'Przedmiot \'' + data['title'] + '\' został dodany.'})
            elif response.status_code == 400:
                message = response.json()['message']
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'error': message})
            elif response.status_code == 401:
                request.session.flush()
                return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Przedmiot \'' + data['title'] + '\' nie został dodany. Sesja użytkownika straciła ważność lub nie masz odpowiednich uprawnień!'})
            else:
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'error': response.status_code})
        return render(request, self.template_name, {'title': self.title, 'form': self.form})

class ListCourseView(View):
    template_name = 'home/list_course.html' 
    title = 'Przedmioty'                      
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Course'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})

        page = 1
        data = {'page': page}

        session = requests.Session()
        session.headers.update({
        'Authorization': 'Bearer '+ request.session['user']['token']
        })
        response = session.get(self.url, params=data, headers={})

        if response.status_code == 200:
            count = int(response.json()['count'])
            if count == 0:
                return render(request, self.template_name, {'title': self.titlex, 'main_info': 'Lista przedmiotów jest pusta.'})
            else:
                lista = dict()
                while count > 10:
                    for x in response.json()['records']:
                        lista[x['id']] = x['title']
                    count -=10
                    page += 1
                    response = session.get(self.url, params={'page': page}, headers={})
                for x in response.json()['records']:
                        lista[x['id']] = x['title']
                return render(request, self.template_name, {'title': self.title, 'lista': lista})
        elif response.status_code == 401:
            request.session.flush()
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Sesja użytkownika straciła ważność lub nie masz odpowiednich uprawnień!'})
        else:
            return render(request, self.template_name, {'title': self.title, 'error': response.status_code})

class RemoveCourseView(View):
    template_name = 'home/list_course.html' 
    title = 'Przedmioty'                      
    context = {'title': title}

    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Course'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})

        session = requests.Session()
        session.headers.update({
        'Authorization': 'Bearer '+ request.session['user']['token']
        })
        response = session.delete(self.url + '/' + kwargs['idCourse'])

        page = 1
        data = {'page': page}

        session = requests.Session()
        session.headers.update({
        'Authorization': 'Bearer '+ request.session['user']['token']
        })
        response = session.get(self.url, params=data, headers={})

        if response.status_code == 200:
            count = int(response.json()['count'])
            if count == 0:
                return render(request, self.template_name, {'title': self.title, 'main_info': 'Lista przedmiotów jest pusta.'})
            else:
                lista = dict()
                while count > 10:
                    for x in response.json()['records']:
                        lista[x['id']] = x['title']
                    count -=10
                    page += 1
                    response = session.get(self.url, params={'page': page}, headers={})
                for x in response.json()['records']:
                        lista[x['id']] = x['title']
                return render(request, self.template_name, {'title': self.title, 'lista': lista})
        elif response.status_code == 401:
            request.session.flush()
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Sesja użytkownika straciła ważność lub nie masz odpowiednich uprawnień!'})
        else:
            return render(request, self.template_name, {'title': self.title, 'error': response.status_code})

class AddExamView(View):
    template_name = 'home/add_exam.html' 
    title = 'Dodaj egzamin'        
    form = AddExamForm()                 
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Exams'
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})
        return render(request, self.template_name, {'title': self.title, 'form': self.form, 'idCourse': kwargs['idCourse']})

    def post(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})
        self.form = AddExamForm(request.POST)
        if self.form.is_valid():
            data = self.form.cleaned_data           
            data['courseId'] = kwargs['idCourse']

            print(data)

            session = requests.Session()
            session.headers.update({
            'Authorization': 'Bearer '+ request.session['user']['token']
            })
            response = session.post(self.url, json=data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return render(request, self.template_name, {'title': self.title, 'form': AddExamForm(), 'idCourse': kwargs['idCourse'], 'info': 'Egzamin \'' + data['description'] + '\' został dodany.'})
            elif response.status_code == 400:
                message = response.json()['message']
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'idCourse': kwargs['idCourse'], 'error': message})
            elif response.status_code == 401:
                request.session.flush()
                return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Egzamin \'' + data['description'] + '\' nie został dodany. Sesja użytkownika straciła ważność lub nie masz odpowiednich uprawnień!'})
            else:
                return render(request, self.template_name, {'title': self.title, 'form': self.form, 'idCourse': kwargs['idCourse'], 'error': response.status_code})
        return render(request, self.template_name, {'title': self.title, 'form': self.form, 'idCourse': kwargs['idCourse']})


class ListExamView(View):
    template_name = 'home/list_exam.html' 
    title = 'Egzaminy'                      
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Exams/course=' 
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})

        session = requests.Session()
        session.headers.update({
        'Authorization': 'Bearer '+ request.session['user']['token']
        })
        response = session.get(self.url + kwargs['idCourse'], headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            count = int(response.json()['count'])
            if count == 0:
                return render(request, self.template_name, {'title': self.title, 'idCourse': kwargs['idCourse'], 'main_info': 'Lista egzaminów jest pusta.'})
            else:
                print(response.json())
                lista = dict()
                for x in response.json()['records']:
                        lista[x['id']] = {'description': x['description'], 'isPassed': x['isPassed']}
                return render(request, self.template_name, {'title': self.title, 'idCourse': kwargs['idCourse'], 'lista': lista})
        elif response.status_code == 401:
            request.session.flush()
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Sesja użytkownika straciła ważność lub nie masz odpowiednich uprawnień!'})
        else:
            return render(request, self.template_name, {'title': self.title, 'error': response.status_code})

class PassExamView(View):
    template_name = 'home/list_exam.html' 
    title = 'Egzaminy'                      
    context = {'title': title}
    
    base_url = 'https://zaliczenie.btry.eu/api/'
    end_point = 'Exams/course=' 
    url = base_url + end_point

    def get(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Nie masz dostępu do tej strony. Musisz się pierwsze zalogować!'})

        session = requests.Session()
        session.headers.update({
        'Authorization': 'Bearer '+ request.session['user']['token']
        })
        response = session.put(self.base_url + 'Exams/' + kwargs['idExam'], headers={'Content-Type': 'application/json'})

        session = requests.Session()
        session.headers.update({
        'Authorization': 'Bearer '+ request.session['user']['token']
        })
        response = session.get(self.url + kwargs['idCourse'], headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            count = int(response.json()['count'])
            if count == 0:
                return render(request, self.template_name, {'title': self.title, 'idCourse': kwargs['idCourse'], 'main_info': 'Lista egzaminów jest pusta.'})
            else:
                print(response.json())
                lista = dict()
                for x in response.json()['records']:
                        lista[x['id']] = {'description': x['description'], 'isPassed': x['isPassed']}
                return render(request, self.template_name, {'title': self.title, 'idCourse': kwargs['idCourse'], 'lista': lista})
        elif response.status_code == 401:
            request.session.flush()
            return render(request, 'home/index.html', {'title': self.title, 'main_error': 'Sesja użytkownika straciła ważność lub nie masz odpowiednich uprawnień!'})
        else:
            return render(request, self.template_name, {'title': self.title, 'idCourse': kwargs['idCourse'], 'error': response.status_code})