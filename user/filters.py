import django_filters
from .models import Classroom, User
from django_filters import ModelMultipleChoiceFilter


class UserFilter(django_filters.FilterSet):
    status = django_filters.BaseInFilter(field_name='status', lookup_expr='in')

    classroom = django_filters.ModelMultipleChoiceFilter(
        field_name='classroom__id',
        queryset=Classroom.objects.all(),
        to_field_name='id',
        conjoined=False
    )

    class Meta:
        model = User
        fields = ['status', 'is_active', 'is_staff', 'classroom']