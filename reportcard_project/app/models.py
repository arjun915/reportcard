from django.db import models

class Class(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Class 5"
    section = models.CharField(max_length=10)  # e.g., "A"

    def __str__(self):
        return str(self.id)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return str(self.id)


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    roll_number = models.IntegerField()
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')

    def __str__(self):
        return str(self.id)


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.FloatField()
    maximum_marks = models.FloatField()
    comment = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)


class Comment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()  # Final Grade/Remarks like "Grade A+ - Pass"

    def __str__(self):
        return str(self.id)
