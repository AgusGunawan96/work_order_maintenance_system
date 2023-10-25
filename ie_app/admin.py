from django.contrib import admin
from ie_app.models import ImpPlanH, ImpPlanD
from .models import ImpPlanH

class ImpPlanHAdmin(admin.ModelAdmin):
    list_display = ('plan_no', 'is_safety_display', 'is_productivity_display', 'is_quality_display', 'is_cost_display')

    def is_safety_display(self, obj):
        return '<input type="radio" disabled="true" {}>'.format('checked' if obj.is_safety else '')
    is_safety_display.short_description = 'Is Safety'
    is_safety_display.allow_tags = True

    def is_productivity_display(self, obj):
        return '<input type="radio" disabled="true" {}>'.format('checked' if obj.is_productivity else '')
    is_productivity_display.short_description = 'Is Productivity'
    is_productivity_display.allow_tags = True

    def is_quality_display(self, obj):
        return '<input type="radio" disabled="true" {}>'.format('checked' if obj.is_quality else '')
    is_quality_display.short_description = 'Is Quality'
    is_quality_display.allow_tags = True

    def is_cost_display(self, obj):
        return '<input type="radio" disabled="true" {}>'.format('checked' if obj.is_cost else '')
    is_cost_display.short_description = 'Is Cost'
    is_cost_display.allow_tags = True

admin.site.register(ImpPlanH, ImpPlanHAdmin)

admin.site.register(ImpPlanD)
