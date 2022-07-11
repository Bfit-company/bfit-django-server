from rest_framework import serializers

from job_type_app.models import JobTypeDB


class JobTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobTypeDB
        fields = '__all__'
