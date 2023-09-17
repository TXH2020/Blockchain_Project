from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username','email','role']
    fieldsets = (
        (('User'), {'fields': ('username','teacher_id','first_name','last_name','email','password','course','semester','branch','subject','role')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Request)
admin.site.register(SubjectCode)
admin.site.register(FinalPapers)