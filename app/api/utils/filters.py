"""Utils to django filters"""
from django.forms import CharField
from django_filters.filters import Filter


class IDField(CharField):
    """ID form field"""


class IDFilter(Filter):
    """Id filter"""
    field_class = IDField
