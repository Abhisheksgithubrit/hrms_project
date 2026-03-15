from django.contrib import admin
from .models import Employee, Attendance

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin configuration for Employee model.
    """
    list_display = ['name', 'email', 'designation', 'department', 'date_of_joining']
    search_fields = ['name', 'email', 'department']
    list_filter = ['department', 'date_of_joining']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Attendance model.
    """
    list_display = ['employee', 'date', 'in_time', 'out_time']
    search_fields = ['employee__name', 'date']
    list_filter = ['date']
