from django.db import models
from django.contrib.auth.models import User
# Create your models here.

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    division = models.ForeignKey(Division,on_delete=models.CASCADE)
    section = models.ForeignKey(Section,on_delete=models.CASCADE)
    employee_number = models.CharField(max_length=8, unique=True)
    employee_ext = models.CharField(max_length=8)

    def __str__(self):
        return self.user.first_name


    
