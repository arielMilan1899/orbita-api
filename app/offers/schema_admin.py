"""Schema admin for offer app"""
from graphene import Field, ID, Int, InputObjectType, List, String, Mutation
from graphene_django.forms.mutation import DjangoModelFormMutation

from accounts.mixins import LoginRequiredMutation
from api.utils.schema import BulkDjangoFormMutation, EditDjangoModelFormMutation
from offers.forms import AdminCreateOfferForm, AdminUpdateOfferForm, AdminControlOfferForm, AdminCreateCategoryForm, \
    AdminUpdateCategoryForm, AdminDeleteCategoryForm, AdminCreateMaterialForm, AdminUpdateMaterialForm, \
    AdminDeleteMaterialForm
from offers.models import Offer, Category, Image, Material
from offers.schema import OfferType, CategoryType, Offers, CategoryQuery, MaterialType


class AdminCategoryType(CategoryType):
    """Type for category model"""

    class Meta:
        """Meta class"""

        model = Category
        fields = ('id', 'order', 'parent_category', 'poster_url', 'poster_public_id')
        use_connection = True

    @classmethod
    def resolve_offers(cls, instance, info, sort=Offer.SortChoices.created_on, **kwargs):  # pylint: disable=W0102
        """Resolve offers"""
        if not isinstance(sort, list):
            sort = [sort]

        if not instance.parent_category:
            return Offer.objects.filter(subcategory__parent_category_id=instance.id)

        return Offer.objects.filter(subcategory_id=instance.id).order_by(*sort)


class ImageInput(InputObjectType):
    """Image input"""
    url = String()
    public_id = String()


class LanguageInput(InputObjectType):
    """Language object type"""

    es = String()
    en = String()


class AdminCreateCategoryMutation(LoginRequiredMutation, DjangoModelFormMutation):
    """
    Mutation to create a category
    """
    category = Field(AdminCategoryType, description='Category instance')

    class Input:
        """Input class"""
        parent_category = ID(required=True)
        title = LanguageInput(required=True)
        description = LanguageInput()

    class Meta:
        """Meta Class"""
        model = Category
        form_class = AdminCreateCategoryForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this AdminCreateCategoryForm
        :type form: AdminCreateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        category = form.save()
        return cls(category=category)


class AdminUpdateCategoryMutation(LoginRequiredMutation, EditDjangoModelFormMutation):
    """
    Mutation to update a category
    """
    category = Field(AdminCategoryType, description='Category instance')

    class Input:
        """Input class"""
        parent_category = ID(required=True)
        title = LanguageInput(required=True)
        description = LanguageInput()

    class Meta:
        """Meta Class"""
        model = Category
        form_class = AdminUpdateCategoryForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateCategoryForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        category = form.save()
        return cls(category=category)


class AdminDeleteCategoryMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to delete a category"""

    class Meta:
        """Meta Class"""
        model = Category
        form_class = AdminDeleteCategoryForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminDeleteCategoryForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        category_id = form.instance.id
        form.delete()
        return category_id


class AdminCreateOfferMutation(LoginRequiredMutation, DjangoModelFormMutation):
    """
    Mutation to create an offer
    """
    offer = Field(OfferType, description='Offer instance')

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminCreateOfferForm

    class Input:
        """Input class"""
        images = List(ImageInput)
        title = LanguageInput(required=True)
        description = LanguageInput()
        materials = List(ID)

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminCreateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer = form.save()
        return cls(offer=offer)


class AdminUpdateOfferMutation(LoginRequiredMutation, EditDjangoModelFormMutation):
    """
    Mutation to update an offer
    """
    offer = Field(OfferType, description='Offer instance')

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminUpdateOfferForm

    class Input:
        """Input class"""
        images = List(ImageInput)
        title = LanguageInput(required=True)
        description = LanguageInput()
        materials = List(ID)

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer = form.save()
        return cls(offer=offer)


class AdminDeleteOfferMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to delete an offer"""

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminControlOfferForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer_id = form.instance.id
        form.delete()
        return offer_id


class AdminActivateOfferMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to activate an offer"""

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminControlOfferForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer_id = form.instance.id
        form.activate(True)
        return offer_id


class AdminDisableOfferMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to deactivate an offer"""

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminControlOfferForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer_id = form.instance.id
        form.activate(False)
        return offer_id


class AdminAddRecommendOfferMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to recommend an offer"""

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminControlOfferForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer_id = form.instance.id
        form.recommend(True)
        return offer_id


class AdminDeleteRecommendOfferMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to deactivate an offer"""

    class Meta:
        """Meta Class"""
        model = Offer
        form_class = AdminControlOfferForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateOfferForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        offer_id = form.instance.id
        form.recommend(False)
        return offer_id


class AdminDeleteImageMutation(Mutation):
    """Mutation to delete an image"""

    class Input:
        public_id = String(required=True)

    public_id = String()

    def mutate(self, info, public_id):
        Image.remove(public_id)
        return AdminDeleteImageMutation(public_id=public_id)


class AdminCreateMaterialMutation(LoginRequiredMutation, DjangoModelFormMutation):
    """
    Mutation to create a material
    """
    material = Field(MaterialType, description='Material instance')

    class Input:
        """Input class"""
        title = LanguageInput(required=True)

    class Meta:
        """Meta Class"""
        model = Material
        form_class = AdminCreateMaterialForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this AdminCreateMaterialForm
        :type form: AdminCreateMaterialForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        material = form.save()
        return cls(material=material)


class AdminUpdateMaterialMutation(LoginRequiredMutation, EditDjangoModelFormMutation):
    """
    Mutation to update a material
    """
    material = Field(MaterialType, description='Material instance')

    class Input:
        """Input class"""
        title = LanguageInput(required=True)

    class Meta:
        """Meta Class"""
        model = Material
        form_class = AdminUpdateMaterialForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateMaterialForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        material = form.save()
        return cls(material=material)


class AdminDeleteMaterialMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to delete a material"""

    class Meta:
        """Meta Class"""
        model = Material
        form_class = AdminDeleteMaterialForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminDeleteMaterialForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        material_id = form.instance.id
        form.delete()
        return material_id


class AdminCategoryQuery(CategoryQuery):
    """
    Root class of the category model queries
    """
    categories = List(AdminCategoryType, description='Return a list of categories')
    category = Field(AdminCategoryType, id=Int(), slug_es=String(), slug_en=String(),
                     description='Return a category instance')


class AdminOfferQuery:
    """Root class of the offer model queries"""
    offer = Field(OfferType, id=Int(), description='Return a offer instance')
    offers = Offers

    @classmethod
    def resolve_offer(cls, instance, info, id, **kwargs):
        """
        Resolve single offer using id.
        :param instance: Query instance
        :param info: Schema info
        :return: OfferType node of Offer model.
        """

        return Offer.objects.get(id=id)

    @classmethod
    def resolve_offers(cls, instance, info, sort=Offer.SortChoices.created_on, **kwargs):  # pylint: disable=W0102
        """Resolve offers"""

        if not isinstance(sort, list):
            sort = [sort]

        return Offer.objects.order_by(*sort)


class AdminOfferMutation:
    """
    Root Class of the offer app mutations
    """
    create_offer = AdminCreateOfferMutation.Field(description='Create a new offer.')
    update_offer = AdminUpdateOfferMutation.Field(description='Update an offer.')
    delete_offer = AdminDeleteOfferMutation.Field(description='Delete an offer.')
    activate_offer = AdminActivateOfferMutation.Field(description='Activate offer.')
    deactivate_offer = AdminDisableOfferMutation.Field(description='Deactivate an offer.')
    create_category = AdminCreateCategoryMutation.Field(description='Create a new category.')
    update_category = AdminUpdateCategoryMutation.Field(description='Update a category.')
    delete_category = AdminDeleteCategoryMutation.Field(description='Delete a category.')
    delete_image = AdminDeleteImageMutation.Field(description='Delete an image from storage.')
    create_material = AdminCreateMaterialMutation.Field(description='Create a material.')
    update_material = AdminUpdateMaterialMutation.Field(description='Update a material.')
    delete_material = AdminDeleteMaterialMutation.Field(description='Delete a material.')
    add_recommend_offer = AdminAddRecommendOfferMutation.Field(description='Add recommend offer.')
    delete_recommend_offer = AdminDeleteRecommendOfferMutation.Field(description='Delete recommend offer.')
