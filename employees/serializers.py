from rest_framework import serializers
from .models import Employee, Attendance


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Employee model.
    """
    class Meta:
        model = Employee
        fields = '__all__'

    def validate_date_of_joining(self, value):
        """
        Ensure the date of joining is not in the future.
        """
        from datetime import date

        if value > date.today():
            raise serializers.ValidationError(
                "Date of joining cannot be in the future."
            )
        return value

    def validate_name(self, value):
        """
        Normalize employee name input.
        """
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name is required.")
        return value

    def validate_department(self, value):
        """
        Normalize department input to avoid duplicate buckets like "IT" vs "IT ".
        """
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Department is required.")
        return value

    def validate_designation(self, value):
        """
        Normalize designation input.
        """
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Designation is required.")
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attendance model.
    """
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

    def validate(self, attrs):
        """
        Validate attendance times for logical consistency.
        """
        in_time = attrs.get('in_time')
        out_time = attrs.get('out_time')

        if out_time is not None and out_time <= in_time:
            raise serializers.ValidationError(
                "Out time must be later than in time."
            )

        return attrs