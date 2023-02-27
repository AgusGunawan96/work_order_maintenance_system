from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# USER START
class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.department_name

class Division(models.Model):
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    division_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.division_name

class Section(models.Model):
    division = models.ForeignKey(Division,on_delete=models.CASCADE)
    section_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.section_name

class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, null=True, blank=True)
    division = models.ForeignKey(Division,on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section,on_delete=models.CASCADE, default=False , related_name = 'sections', null=True, blank=True)
    employee_ext = models.CharField(max_length=8, blank=True, null=True)
    is_supervisor = models.BooleanField(default=False, blank=True, null=True)
    is_manager = models.BooleanField(default=False, blank=True, null=True)
    is_bod = models.BooleanField(default=False, blank=True, null=True)
    position = models.CharField(max_length=128, unique=False, default=False, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True, null=True)
    
    def __str__(self):
        return self.user.first_name
    





    
