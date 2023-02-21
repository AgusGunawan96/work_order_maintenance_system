from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TicketStatus(models.TextChoices):
    IN_APPROVAL_SUPERVISOR = 'In Approval Supervisor'
    IN_APPROVAL_MANAGER = 'In Approval Manager'
    IN_APPROVAL_IT = 'Pending'
    IN_PROGRESS = 'In Progress'
    IN_REVIEW = 'In Review'
    DONE = 'Done'

class Ticket(models.Model):
    title = models.CharField(max_length=100)
    assignee = models.ForeignKey(User, null=True, blank = True, on_delete=models.CASCADE)
    status = models.CharField(max_length=25, choices=TicketStatus.choices, default=TicketStatus.IN_APPROVAL_SUPERVISOR)
    description = models.TextField()
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)