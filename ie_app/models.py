from django.db import models
from django.contrib.auth.models import User
from master_app.models import UserKeluargaInfo, UserProfileInfo
from django.utils import timezone
# Create your models here.

# Employee Information system START

# Buat database Training history
# Buat Database Experience (Section or Dept) history

# Employee Information system END

class ImpPlanH(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    plan_no             = models.CharField(max_length=128, null=True, blank=True)
    duedate             = models.DateTimeField('Due date', null=True, blank=True)
    classification      = models.CharField(max_length=128, null=True, blank=True)
    created_at          = models.DateTimeField('created at', auto_now_add=True)
    updated_at          = models.DateTimeField('updated at', auto_now=True)
    def __str__(self) :
        return self.plan_no
    
class ImpPlanD(models.Model):
    planh               = models.ForeignKey(ImpPlanH, null=True, blank=True, on_delete=models.CASCADE)
    plan_no             = models.CharField(max_length=128, null=True, blank=True)
    problem_desc        = models.TextField(blank=True, null=True)
    improvement_desc    = models.TextField(blank=True, null=True)
    target_desc         = models.TextField(blank=True, null=True)
    benefit_desc        = models.TextField(blank=True, null=True)
    created_at          = models.DateTimeField('created at', auto_now_add=True)
    updated_at          = models.DateTimeField('updated at', auto_now=True)
    def __str__(self) :
        return self.plan_no