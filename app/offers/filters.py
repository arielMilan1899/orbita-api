""""FilterSet of paid_ad app"""
import django_filters
from django.db.models import Q

from api.utils.filters import IDFilter
from offers.models import Offer, Material


class OfferFilter(django_filters.FilterSet):
    """Base filter set for Offer"""

    class Meta:
        """Meta class"""
        model = Offer
        fields = []

    id = IDFilter(field_name='id', label='FilterById')
    subcategory = IDFilter(field_name='subcategory__id', label='FilterBySubCategory')
    parent_category = IDFilter(method='filter_by_parent_category', label='FilterByParentCategory')
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='FilterByPriceGte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='FilterByPriceLte')
    title_description = django_filters.CharFilter(method='filter_by_title_description',
                                                  label='FilterByTitleDescription')
    materials = django_filters.ModelMultipleChoiceFilter(field_name='offersmaterial__material',
                                                         label='FilterByMaterial',
                                                         queryset=Material.objects.all())
    recommended = django_filters.BooleanFilter(field_name='recommended', label='FilterByRecommended')

    @classmethod
    def filter_by_parent_category(cls, queryset, name, value):
        """
        Filter offer by its parent_category.
        :param queryset: Current queryset
        :param name: Field name. Expected to be `offer_type`
        :param value: Field value
        :type queryset: django.db.models.QuerySet
        :return: QuerySet with the filter applied
        """
        query = Q(subcategory__parent_category__id=value)
        return queryset.filter(query)

    @classmethod
    def filter_by_title_description(cls, queryset, name, value):
        """
        Filter offer by its title and description.
        :param queryset: Current queryset
        :param name: Field name. Expected to be `offer_type`
        :param value: Field value
        :type queryset: django.db.models.QuerySet
        :return: QuerySet with the filter applied
        """
        title_query = Q(title_es__icontains=value) | Q(title_en__icontains=value)
        description_query = Q(description_es__icontains=value) | Q(description_en__icontains=value)
        return queryset.filter(title_query | description_query)
