from rest_framework import serializers
from .models import Student, Class, Subject, Mark, Comment

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'

class FinalCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
