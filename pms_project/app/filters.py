from django_filters import rest_framework as filters
import rest_framework_filters as rest_filters
from django.db.models import Sum, Window, Avg, F, Max
from app.models import RpmReading
import datetime
from django.utils import timezone
import pytz
import pdb


class RpmReadingsFilter(filters.FilterSet):
    machine_no = filters.CharFilter(method='meters_sum_func')
    last_minutes = filters.CharFilter(method='last_minutes_func')
    
#testing pull request

    def meters_sum_func(self, queryset, name, value):
        return queryset.filter(machine_no=value).annotate(total=Window(expression=Sum('meters')))

    def last_minutes_func(self, queryset, name, value):
        now = timezone.now()
        earlier = timezone.now() - datetime.timedelta(minutes=int(value))
        return queryset.filter(time__range=(earlier, now))


    class Meta:
        model = RpmReading
        fields = ['machine_no', 'loom', "time"]

