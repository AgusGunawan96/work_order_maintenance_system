from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# FUNCTION START
class GenderField(models.CharField):
    MALE = 'M'
    FEMALE = 'F'
    NONBINARY = 'NB'
    CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NONBINARY, 'Non-binary'),
    ]
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', self.CHOICES)
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == 2:
            del kwargs['max_length']
        if kwargs.get('choices') == self.CHOICES:
            del kwargs['choices']
        return name, path, args, kwargs
# FUNCTION END

# USER START
class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.department_name

class Division(models.Model):
    department      = models.ForeignKey(Department,on_delete=models.CASCADE)
    division_name   = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.division_name

class Section(models.Model):
    division        = models.ForeignKey(Division,on_delete=models.CASCADE)
    section_name    = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.section_name

class UserProfileInfo(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    department      = models.ForeignKey(Department,on_delete=models.CASCADE, null=True, blank=True)
    division        = models.ForeignKey(Division,on_delete=models.CASCADE, null=True, blank=True)
    section         = models.ForeignKey(Section,on_delete=models.CASCADE, default=False , related_name = 'sections', null=True, blank=True)
    employee_ext    = models.CharField(max_length=8, blank=True, null=True)
    is_supervisor   = models.BooleanField(default=False, blank=True, null=True)
    is_manager      = models.BooleanField(default=False, blank=True, null=True)
    is_bod          = models.BooleanField(default=False, blank=True, null=True)
    is_contract     = models.BooleanField(default=False, blank=True, null=True)
    is_permanent    = models.BooleanField(default=False, blank=True, null=True)
    gender          = GenderField(default='NB')
    position        = models.CharField(max_length=128, unique=False, default=False, blank=True, null=True)
    profile_pic     = models.ImageField(upload_to='profile_pics',blank=True, null=True)

class Notification(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp   = models.DateTimeField(auto_now_add = True)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    link        = models.CharField(max_length=128, unique=True)
    category    = models.CharField(max_length=128, unique=True, default=False)





    
