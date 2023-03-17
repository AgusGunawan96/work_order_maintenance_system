from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class TicketStatus(models.TextChoices):
    IN_PROGRESS = 'In Progress'
    IN_REVIEW   = 'In Review'
    DONE        = 'Done'

class TicketType(models.TextChoices):
    REQUEST_APPLICATION     = 'Request Application'
    REQUEST_HARDWARE        = 'Request Hardware'
    REQUEST_EMERGENCY       = 'Request Emergency'
    REQUEST_DOCUMENT_DATA   = 'Request Document Data'
    PROBLEM_HARDWARE        = 'Problem Hardware'
    PROBLEM_SOFTWARE        = 'Problem Software'

class TicketPriority(models.TextChoices):
    LOW     = 'Low'
    Middle  = 'Middle'
    High    = 'High'

class TicketOrder(models.TextChoices):
    NEW                     = 'New'
    RENEWAL_OR_MODIFICATION = 'Renewal Or Modification'
    LENING                  = 'Lening'
    PROBLEM                 = 'Problem'
    
class Software(models.Model):
    name        = models.CharField(max_length=100)
    created_at  = models.DateTimeField('created at', auto_now_add=True, null=True, blank=True)
    updated_at  = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.name
    
class HardwareType(models.Model):
    name        = models.CharField(max_length=100)
    created_at  = models.DateTimeField('created at', auto_now_add=True, null=True, blank=True)
    updated_at  = models.DateTimeField('updated at', auto_now=True)
    
    def __str__(self):
        return self.name
    
class Hardware(models.Model):
    hardware    = models.ForeignKey(HardwareType, null=True, blank=True, on_delete=models.CASCADE)
    name        = models.CharField(max_length=100)
    quantity    = models.PositiveIntegerField(blank=True, default=0)
    created_at  = models.DateTimeField('created at', auto_now_add=True, null=True, blank=True)
    updated_at  = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.name
    
class HardwareInfo(models.Model):
    hardware    = models.ForeignKey(Hardware, null=True, blank=True, on_delete=models.CASCADE)
    nomor_po    = models.CharField(max_length=64, null=True, blank=True)
    quantity    = models.PositiveIntegerField(null=True, blank=True)
    kode_barang = models.CharField(max_length=64, null=True, blank=True)
    created_at  = models.DateTimeField('created at', auto_now_add=True, null=True, blank=True)
    updated_at  = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.nomor_po

class Ticket(models.Model):
    assignee    = models.ForeignKey(User, null=True, blank = True, on_delete=models.CASCADE)
    hardware    = models.ForeignKey(Hardware, on_delete=models.CASCADE, blank=True, null=True)
    software    = models.ForeignKey(Software, on_delete=models.CASCADE, blank=True, null=True)
    title       = models.CharField(max_length=100)
    type        = models.CharField(max_length=25, choices=TicketType.choices, null=True)
    order       = models.CharField(max_length=25, choices=TicketOrder.choices, null=True)
    description = models.TextField()
    quantity    = models.PositiveIntegerField(blank=True, default=0)
    created_at  = models.DateTimeField('created at', auto_now_add=True)
    updated_at  = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.title

class TicketAttachment(models.Model):
    Ticket      = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=True, null=True)
    attachment  = models.FileField(upload_to='TicketAttachments/', null=False, blank=True)

class TicketApprovalSupervisor(models.Model):
    ticket                      = models.OneToOneField(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    supervisor                  = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_supervisor       = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_supervisor      = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_supervisor    = models.TextField( blank=True, null=True)
    created_at                  = models.DateTimeField( auto_now_add=True)
    updated_at                  = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.ticket.title

class TicketApprovalManager(models.Model):
    ticket_approval_supervisor  = models.OneToOneField(TicketApprovalSupervisor, on_delete=models.CASCADE, null=True, blank=True)
    manager                     = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_approve_manager          = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_manager         = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_manager       = models.TextField(blank=True, null=True)
    created_at                  = models.DateTimeField( auto_now_add=True)
    updated_at                  = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.ticket_approval_supervisor.ticket.title
    
class TicketApprovalIT(models.Model):
    ticket_approval_manager = models.OneToOneField(TicketApprovalManager, on_delete=models.CASCADE, null=True, blank=True)
    it                      = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_approve_it           = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_it          = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_it        = models.TextField(blank=True, null=True)
    created_at              = models.DateTimeField( auto_now_add=True)
    updated_at              = models.DateTimeField( auto_now=True)
    def __str__(self):
        return self.ticket_approval_manager.ticket_approval_supervisor.ticket.title


class TicketProgressIT(models.Model):
    ticket_approval_it  = models.OneToOneField(TicketApprovalIT, on_delete=models.CASCADE, null=True, blank=True)
    ticket_no           = models.CharField(max_length=128, null=True, blank=True)
    status              = models.CharField(max_length=25, choices=TicketStatus.choices, default=TicketStatus.IN_PROGRESS)
    priority            = models.CharField(max_length=25, choices=TicketPriority.choices, default=TicketPriority.LOW)
    cost                = models.PositiveBigIntegerField(null=True, blank=True)
    review_description  = models.TextField(blank=True, null=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.ticket_approval_it.ticket_approval_manager.ticket_approval_supervisor.ticket.title


