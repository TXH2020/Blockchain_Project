from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', auth_views.LoginView.as_view(template_name="login.html"),name='login'),
	path('logout',views.user_logout,name='user_logout'),
	path('teacher',views.teacher_dashboard,name='teacher_dashboard'),
	path('COE',views.coe_dashboard,name='coe_dashboard'),
	path('superintendent',views.st_dashboard,name='st_dashboard'),
	path('user_login',views.user_login,name="user_login"),
	path('get_teachers',views.get_teachers,name="get_teachers"),
	path('add_teacher',views.add_teacher,name='add_teacher')
]
