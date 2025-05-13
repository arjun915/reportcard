from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,redirect
from .models import Student, Class, Subject, Mark, Comment
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from rest_framework import status

@api_view(["POST"])
def add_student_api(request):
    data = request.data
    try:
        # Extract student info
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        roll_number = data.get("roll_number")
        class_id = data.get("class_id")
        subjects_data = data.get("subjects", [])

        class_instance = get_object_or_404(Class, id=class_id)

        # Create student
        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            roll_number=roll_number,
            class_ref=class_instance
        )

        # Add marks
        for subject_data in subjects_data:
            subject_id = subject_data.get("subject_id")
            marks_obtained = subject_data.get("marks_obtained")
            maximum_marks = subject_data.get("maximum_marks")
            comment = subject_data.get("comment")

            subject = get_object_or_404(Subject, id=subject_id)
            Mark.objects.create(
                student=student,
                subject=subject,
                marks_obtained=marks_obtained,
                maximum_marks=maximum_marks,
                comment=comment
            )

        return Response({
            "status": "success",
            "message": "Student data saved successfully"
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def get_report_card_api(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    marks = Mark.objects.filter(student=student)

    subject_data = []
    for mark in marks:
        subject_data.append({
            "subject_name": mark.subject.name,
            "marks_obtained": mark.marks_obtained,
            "maximum_marks": mark.maximum_marks,
            "comment": mark.comment
        })

    data = {
        "status": "success",
        "student": {
            "first_name": student.first_name,
            "last_name": student.last_name,
            "roll_number": student.roll_number,
            "class": student.class_ref.name,
            "section": student.class_ref.section
        },
        "subjects": subject_data
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
def generate_reportcard_link(request):
    student_id = request.data.get("student_id")

    if not student_id:
        return Response({
            "status": "error",
            "message": "Student ID is required"
        }, status=400)

    student = get_object_or_404(Student, id=student_id)

    # Generate full URL to existing PDF download view
    file_url = request.build_absolute_uri(
        reverse('download_pdf', args=[student_id])
    )

    return Response({
        "status": "success",
        "message": "Report card generated",
        "fileUrl": file_url
    })


def calculate_grade(marks_queryset):
    total = sum([m.marks_obtained for m in marks_queryset])
    max_total = sum([m.maximum_marks for m in marks_queryset])
    percentage = (total / max_total) * 100 if max_total else 0

    if percentage >= 90:
        return "Grade A+ - Pass"
    elif percentage >= 75:
        return "Grade A - Pass"
    elif percentage >= 60:
        return "Grade B - Pass"
    elif percentage >= 40:
        return "Grade C - Pass"
    else:
        return "Grade F - Fail"

# UI Views (non-API)
def student_list_view(request):
    # students = Student.objects.all()
    students = Student.objects.all().select_related('class_ref')  # Add select_related for efficiency

    return render(request, "app/student_list.html", {"students": students})

def student_report_preview(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    marks = Mark.objects.filter(student=student)
    grade = calculate_grade(marks)
    final_comment = Comment.objects.filter(student=student).first()

    return render(request, "report_preview.html", {
        "student": student,
        "marks": marks,
        "grade": grade,
        "final_comment": final_comment.comment if final_comment else "",
    })

def add_student_view(request):
    if request.method == 'POST':
        try:
            # Extract student data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            roll_number = request.POST.get('roll_number')
            class_name = request.POST.get('class_name')
            section = request.POST.get('section')

            # Create class and student
            class_instance, _ = Class.objects.get_or_create(name=class_name, section=section)
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                roll_number=roll_number,
                class_ref=class_instance
            )

            # Get all subject data from POST
            subject_names = request.POST.getlist('subject_name[]')
            marks_obtained = request.POST.getlist('marks_obtained[]')
            max_marks = request.POST.getlist('maximum_marks[]')
            comments = request.POST.getlist('mark_comment[]')  # Changed to match form

            # Create subjects and marks
            for name, mark, max_mark, comment in zip(subject_names, marks_obtained, max_marks, comments):
                subject, _ = Subject.objects.get_or_create(name=name, class_ref=class_instance)
                Mark.objects.create(
                    student=student,
                    subject=subject,
                    marks_obtained=mark,
                    maximum_marks=max_mark,
                    comment=comment
                )

            return redirect('students_list')  # Make sure this URL name is correct

        except Exception as e:
            # Add error handling (you might want to show this to the user)
            print(f"Error: {e}")
            return render(request, 'app/student_form.html', {'error': str(e)})

    return render(request, 'app/student_form.html')

def view_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    marks = Mark.objects.filter(student=student)
    grade = calculate_grade(marks)
    final_comment = Comment.objects.filter(student=student).first()

    context = {
        "student": student,
        "marks": marks,
        "final_comment": final_comment.comment if final_comment else "",
        "grade": grade,
    }
    return render(request, 'app/view_report.html', context)

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student.first_name = request.POST.get("first_name")
        student.last_name = request.POST.get("last_name")
        student.roll_number = request.POST.get("roll_number")
        student.save()
        return redirect('students_list')

    context = {
        "student": student
    }
    return render(request, 'app/edit_student.html', context)

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, 'Student deleted successfully!')
    return redirect('students_list')


def download_report_card_pdf(request, student_id):
    student = Student.objects.get(id=student_id)
    marks = Mark.objects.filter(student=student)
    final_comment = Comment.objects.filter(student=student).first()

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=ReportCard_{student.first_name}_{student.last_name}.pdf'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 50, "Student Report Card")

    # Student Info
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, f"Name: {student.first_name} {student.last_name}")
    p.drawString(100, height - 120, f"Roll Number: {student.roll_number}")
    p.drawString(100, height - 140, f"Class: {student.class_ref.name} - {student.class_ref.section}")

    # Table headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 180, "Subject")
    p.drawString(250, height - 180, "Marks Obtained")
    p.drawString(400, height - 180, "Maximum Marks")
    p.drawString(500, height - 180, "Comment")

    # Marks Table
    y = height - 200
    p.setFont("Helvetica", 11)
    for mark in marks:
        p.drawString(100, y, mark.subject.name)
        p.drawString(250, y, str(mark.marks_obtained))
        p.drawString(400, y, str(mark.maximum_marks))
        p.drawString(500, y, mark.comment if mark.comment else "-")
        y -= 20

    # Grade
    grade = calculate_grade(marks)

    # Final Comments & Grade
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Grade: " + grade)
    y -= 20
    if final_comment:
        p.drawString(100, y, "Final Comment: " + final_comment.comment)

    p.showPage()
    p.save()
    return response

