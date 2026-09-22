from django.contrib import admin
from .domain.models import Assessment, AssessmentSection, AssessmentSectionAnswer, AssessmentStudentResult, AssessmentStudentResponse, AssessmentStudentStatus, MockExam, ProgressTrack

admin.site.register(Assessment)
admin.site.register(AssessmentSection)
admin.site.register(AssessmentSectionAnswer)
admin.site.register(AssessmentStudentResult)
admin.site.register(AssessmentStudentResponse)
admin.site.register(AssessmentStudentStatus)
admin.site.register(MockExam)
admin.site.register(ProgressTrack)
