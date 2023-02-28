from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class TicketStatus(models.TextChoices):
    IN_PROGRESS = 'In Progress'
    IN_REVIEW = 'In Review'
    DONE = 'Done'

class TicketType(models.TextChoices):
    REQUEST = 'Request'
    PROBLEM = 'Problem'
    OTHER   = 'Other'

class TicketPriority(models.TextChoices):
    LOW = 'Low'
    Middle = 'Middle'
    High = 'High'

class Hardware(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(blank=True, default=0)

    def __str__(self):
        return self.name
    
class HardwareInfo(models.Model):
    Hardware = models.ForeignKey(Hardware, null=True, blank=True, on_delete=models.CASCADE)
    nomor_po = models.CharField(max_length=64, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    kode_barang = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.nomor_po

class Ticket(models.Model):
    title = models.CharField(max_length=100)
    assignee = models.ForeignKey(User, null=True, blank = True, on_delete=models.CASCADE)
    type = models.CharField(max_length=25, choices=TicketType.choices, default=TicketType.OTHER)
    description = models.TextField()
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, default=0)
    ticket_pic = models.ImageField(upload_to='ticket_pics', blank=True)
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.title



class TicketApprovalSupervisor(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_supervisor = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_supervisor = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_supervisor = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.ticket.title

class TicketApprovalManager(models.Model):
    ticket_approval_supervisor = models.OneToOneField(TicketApprovalSupervisor, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_approve_manager = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_manager = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_manager = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.ticket_approval_supervisor.ticket.title
    
class TicketApprovalIT(models.Model):
    ticket_approval_manager = models.OneToOneField(TicketApprovalManager, on_delete=models.CASCADE, null=True, blank=True)
    it = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_approve_it = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_it = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_it = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)
    def __str__(self):
        return self.ticket_approval_manager.ticket_approval_supervisor.ticket.title


class TicketProgressIT(models.Model):
    ticket_approval_it = models.OneToOneField(TicketApprovalIT, on_delete=models.CASCADE, null=True, blank=True)
    ticket_no =models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=25, choices=TicketStatus.choices, default=TicketStatus.IN_PROGRESS)
    priority = models.CharField(max_length=25, choices=TicketPriority.choices, default=TicketPriority.LOW)
    review_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.ticket_approval_it.ticket_approval_manager.ticket_approval_supervisor.ticket.title


