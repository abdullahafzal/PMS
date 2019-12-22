from django_filters import rest_framework as filters
import rest_framework_filters as rest_filters
from django.db.models import Sum, Window, Avg, F, Max
from app.models import RpmReading
import datetime
from django.utils import timezone
import pytz



class RpmReadingsFilter(filters.FilterSet):
    test = filters.CharFilter(method='meters_sum')
    last_minutes = filters.CharFilter(method='meters_sum')

    def meters_sum(self, queryset, name, value):
        # ----- HOW TO GET VALUE OF LAST_MINUTES FROM QUREY PARRAMETERS HER
        now = timezone.now()
        earlier = timezone.now() - datetime.timedelta(minutes=915)
        return queryset.filter(time__range=(earlier, now)).filter(machine_no=value).annotate(total=Window(expression=Sum('meters')))

    class Meta:
        model = RpmReading
        fields = ['machine_no', 'loom', "time"]



#     class Meta:
#         model = RpmReading
#         fields=['machine_no', 'loom', "time", "test"]
#
#     def test(self, name, value, queryset):
#         print("test method")
#         return queryset.filter(machine_no=value).aggregate(Sum('meters'))
