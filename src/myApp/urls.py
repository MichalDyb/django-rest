"""myApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views as home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home.IndexView.as_view(), name='home_index'),
    path('login/', home.LoginView.as_view(), name='home_login'),
    path('register/', home.RegisterView.as_view(), name='home_register'),
    path('logout/', home.LogoutView.as_view(), name='home_logout'),
    path('add_course/', home.AddCourseView.as_view(), name='home_add_course'),
    path('list_course/', home.ListCourseView.as_view(), name='home_list_course'),
    path('remove_course/<str:idCourse>/', home.RemoveCourseView.as_view(), name='home_remove_course'),
    path('add_exam/<str:idCourse>/', home.AddExamView.as_view(), name='home_add_exam'),
    path('list_exam/<str:idCourse>/', home.ListExamView.as_view(), name='home_list_exam'),
    path('pass_exam/<str:idCourse>/<str:idExam>/', home.PassExamView.as_view(), name='home_pass_exam'),
]
