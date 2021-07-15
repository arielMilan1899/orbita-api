"""Schema for offer app"""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from api.utils.schema import django_choice_to_type
from offers.exceptions import CategoryDoesNotExist
from offers.filters import OfferFilter
from offers.models import Category, Offer, Image, Material, OffersMaterial

SortChoices = django_choice_to_type('SortChoices', Offer.SortChoices)  # pylint: disable=C0103


class LanguageType(graphene.ObjectType):
    """Language object type"""

    es = graphene.String()
    en = graphene.String()


class ImageType(DjangoObjectType):
    """Image Model Type with all data needed to fetch the image"""

    class Meta:
        """Meta Class"""
        model = Image
        fields = ('id', 'public_id', 'url')
        use_connection = True


class MaterialType(DjangoObjectType):
    """Material Model Type with all data needed to fetch the material"""

    title = graphene.Field(LanguageType)

    class Meta:
        """Meta Class"""
        model = Material
        fields = ('id',)
        use_connection = True

    def resolve_title(self, info, **kwargs):
        """Resolve title"""
        return LanguageType(es=self.title_es, en=self.title_en)


class OfferType(DjangoObjectType):
    """Type for offer model"""

    images = graphene.List(ImageType, description='Offer images list')
    materials = graphene.List(MaterialType, description='Offer materials list')
    title = graphene.Field(LanguageType)
    description = graphene.Field(LanguageType)
    short_description = graphene.Field(LanguageType)
    slug = graphene.Field(LanguageType)
    permalink = graphene.Field(LanguageType)

    class Meta:
        """Meta class"""

        model = Offer
        fields = ('id', 'price', 'subcategory', 'on_sale', 'created_on', 'updated_on', 'recommended',)
        use_connection = True

    def resolve_images(self, info, **kwargs):
        """Resolve list of images"""
        return self.image_set.all()

    def resolve_materials(self, info, **kwargs):
        """Resolve list of materials"""
        return [offers_material.material for offers_material in self.offersmaterial_set.all()]

    def resolve_title(self, info, **kwargs):
        """Resolve title"""
        return LanguageType(es=self.title_es, en=self.title_en)

    def resolve_description(self, info, **kwargs):
        """Resolve description"""
        return LanguageType(es=self.description_es, en=self.description_en)

    def resolve_short_description(self, info, **kwargs):
        """Resolve short_description"""
        return LanguageType(es=self.short_description_es, en=self.short_description_en)

    def resolve_slug(self, info, **kwargs):
        """Resolve slug"""
        return LanguageType(es=self.slug_es, en=self.slug_en)

    def resolve_permalink(self, info, **kwargs):
        """Resolve permalink"""
        return LanguageType(es=self.permalink_es, en=self.permalink_en)


Offers = DjangoFilterConnectionField(OfferType, filterset_class=OfferFilter,
                                     sort=graphene.Argument(graphene.List(SortChoices)),
                                     description='Category offers')


class CategoryType(DjangoObjectType):
    """Type for category model"""

    class Meta:
        """Meta class"""

        model = Category
        fields = ('id', 'order', 'parent_category', 'poster_url', 'poster_public_id')
        use_connection = True

    # pylint: disable=E0602
    subcategories = graphene.List(lambda: CategoryType, description='Subcategories children of this category')
    offers = Offers
    materials = graphene.List(MaterialType, description='Offers materials list')
    title = graphene.Field(LanguageType)
    description = graphene.Field(LanguageType)
    slug = graphene.Field(LanguageType)

    def resolve_subcategories(self, info):
        """
        Resolve all subcategories of a given category.
        :param info: Schema info
        """
        return self.category_set.all().order_by('order')

    @classmethod
    def resolve_offers(cls, instance, info, sort=Offer.SortChoices.created_on, **kwargs):  # pylint: disable=W0102
        """Resolve offers"""
        if not isinstance(sort, list):
            sort = [sort]

        if not instance.parent_category:
            return Offer.objects.filter(on_sale=True).filter(subcategory__parent_category_id=instance.id)

        return Offer.objects.filter(on_sale=True).filter(subcategory_id=instance.id).order_by(*sort)

    def resolve_title(self, info, **kwargs):
        """Resolve title"""
        return LanguageType(es=self.title_es, en=self.title_en)

    def resolve_description(self, info, **kwargs):
        """Resolve description"""
        return LanguageType(es=self.description_es, en=self.description_en)

    def resolve_slug(self, info, **kwargs):
        """Resolve slug"""
        return LanguageType(es=self.slug_es, en=self.slug_en)

    def resolve_materials(self, info, **kwargs):
        """Resolve list of materials"""

        if not self.parent_category:
            return set([offers_material.material for offers_material in
                        OffersMaterial.objects.filter(offer__subcategory__parent_category_id=self.id)])

        return set([offers_material.material for offers_material in
                    OffersMaterial.objects.filter(offer__subcategory_id=self.id)])


class CategoryQuery:
    """
    Root class of the category model queries
    """
    categories = graphene.List(CategoryType, description='Return a list of categories')
    category = graphene.Field(CategoryType, id=graphene.Int(), slug_es=graphene.String(), slug_en=graphene.String(),
                              description='Return a category instance')

    @classmethod
    def resolve_categories(cls, instance, info):
        """
        Resolve all categories
        :param instance: Query instance
        :param info: Schema info
        :return: All parent categories
        """
        return Category.objects.filter(parent_category=None).order_by('order')

    @classmethod
    def resolve_category(cls, instance, info, **kwargs):
        """
        Resolve single category using id or slug.
        :param instance: Query instance
        :param info: Schema info
        :return: CategoryType node of Category model.
        """
        id_is_arg = 'id' in kwargs
        slug_es_is_arg = 'slug_es' in kwargs
        slug_en_is_arg = 'slug_en' in kwargs

        if id_is_arg and slug_es_is_arg and slug_en_is_arg or not (id_is_arg or slug_es_is_arg or slug_en_is_arg):
            raise CategoryDoesNotExist()

        if id_is_arg:
            args = {'id': kwargs['id']}
        elif slug_es_is_arg:
            args = {'slug_es': kwargs['slug_es']}
        else:
            args = {'slug_en': kwargs['slug_en']}

        return Category.objects.get(**args)


class OfferQuery:
    """Root class of the offer model queries"""
    offer = graphene.Field(OfferType, id=graphene.Int(), description='Return a offer instance')
    offers = Offers

    @classmethod
    def resolve_offer(cls, instance, info, id, **kwargs):
        """
        Resolve single offer using id.
        :param instance: Query instance
        :param info: Schema info
        :return: OfferType node of Offer model.
        """

        return Offer.objects.filter(on_sale=True).get(id=id)

    @classmethod
    def resolve_offers(cls, instance, info, sort=Offer.SortChoices.created_on, **kwargs):  # pylint: disable=W0102
        """Resolve offers"""

        if not isinstance(sort, list):
            sort = [sort]

        return Offer.objects.filter(on_sale=True).order_by(*sort)


class MaterialQuery:
    """
    Root class of the material model queries
    """
    materials = graphene.List(MaterialType, description='Return a list of materials')

    @classmethod
    def resolve_materials(cls, instance, info):
        """
        Resolve all materials
        :param instance: Query instance
        :param info: Schema info
        :return: All materials
        """
        return Material.objects.all()
