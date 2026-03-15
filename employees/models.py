from django.db import models


class Employee(models.Model):
    """
    Model representing an employee in the HRMS system.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    date_of_joining = models.DateField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Attendance(models.Model):
    """
    Model representing attendance records for employees.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    in_time = models.TimeField()
    out_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date']
