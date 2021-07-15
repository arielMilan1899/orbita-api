"""Forms for offer app"""
from django.db.models import Q
from django.forms import ModelForm, forms
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from offers.models import Offer, Category, Image, OffersMaterial, Material

INVALID_CATEGORY_NAME = _('Category name already exist')
INVALID_CATEGORY = _('Category doest exist')
INVALID_SUBCATEGORY = _('Category should be a subcategory')


class AdminCreateCategoryForm(ModelForm):
    """
    Form to create a category from admin
    """

    class Meta:
        """Meta class"""
        model = Category
        fields = ['order', 'poster_url', 'poster_public_id']

    def clean_title(self):
        """Validate title_es"""

        title = self.data['title']
        slug_es = slugify(title.es)
        slug_en = slugify(title.en)

        query = Q(slug_es=slug_es) | Q(slug_en=slug_en)

        query = Category.objects.filter(query)

        if self.instance.id:
            query = query.exclude(id=self.instance.id)

        if query.exists():
            raise forms.ValidationError(INVALID_CATEGORY_NAME, code='invalid')

        self.instance.title_es = title.es
        self.instance.title_en = title.en

    def clean(self):
        """validate form"""

        self.clean_title()

        parent_category = int(self.data['parent_category'])

        if parent_category == 0:
            parent_category = None

        if parent_category and \
                (parent_category == self.instance.id or not Category.objects.filter(id=parent_category).exists()):
            raise forms.ValidationError(INVALID_CATEGORY, code='invalid')

        self.instance.parent_category_id = parent_category

        if 'description' in self.data:
            self.instance.description_es = self.data['description'].es
            self.instance.description_en = self.data['description'].en

    def save(self, commit=True):
        """Save form"""

        category = super(AdminCreateCategoryForm, self).save(commit=commit)

        if category.parent_category is None:
            for subcategory in category.category_set.all():
                subcategory.save()
                for offer in subcategory.offer_set.all():
                    offer.save()
        else:
            for offer in category.offer_set.all():
                offer.save()

        return category


class AdminUpdateCategoryForm(AdminCreateCategoryForm):
    """
    Form to update a category from admin
    """

    def __init__(self, *args, **kwargs):
        super(AdminUpdateCategoryForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False

    class Meta:
        """Meta class"""
        model = Category
        fields = AdminCreateCategoryForm.Meta.fields

    def clean(self):

        cleaned_data = super(AdminUpdateCategoryForm, self).clean()

        if self.instance.poster_public_id != self.cleaned_data.get('poster_public_id', None):
            Image.remove(self.instance.poster_public_id)

        return cleaned_data


class AdminDeleteCategoryForm(ModelForm):
    """
    Form to delete a category from admin
    """

    class Meta:
        """Meta class"""
        model = Category
        fields = []

    def delete(self):
        """Delete offer"""
        Image.remove(self.instance.poster_public_id)

        if not self.instance.parent_category:
            for subcategory in self.instance.category_set.all():
                Image.remove(subcategory.poster_public_id)

            for offer in Offer.objects.filter(subcategory__parent_category_id=self.instance.id):
                images = Image.objects.filter(offer_id=offer.id)
                for image in images:
                    Image.remove(public_id=image.public_id)

        else:
            for offer in Offer.objects.filter(subcategory_id=self.instance.id):
                images = Image.objects.filter(offer_id=offer.id)
                for image in images:
                    Image.remove(public_id=image.public_id)

        self.instance.delete()


class AdminCreateOfferForm(ModelForm):
    """
    Form to create an offer from admin
    """

    class Meta:
        """Meta class"""
        model = Offer
        fields = ['subcategory', 'currency', 'price', 'recommended']

    def clean_subcategory(self):
        """Validate subcategory is actually a subcategory, not a parent category"""
        subcategory = self.cleaned_data['subcategory']

        # If subcategory does not have a parent category, then it is a parent category.
        if subcategory.parent_category is None:
            raise forms.ValidationError(INVALID_SUBCATEGORY, code='invalid')
        return subcategory

    def clean_images(self, offer):
        """Clean images"""
        images = self.data.get('images', [])

        current_images = Image.objects.filter(offer_id=offer.id)

        if current_images:
            excluded_images = current_images.exclude(public_id__in=[image.public_id for image in images])

            for image in excluded_images:
                Image.remove(image.public_id)
                image.delete()

            current_public_ids = [image.public_id for image in current_images]
            images = [image for image in images if image.public_id not in current_public_ids]

        for image in images:
            Image.objects.create(offer=offer, url=image.url, public_id=image.public_id)

    def clean_materials(self, offer):
        """Clean materials"""
        materials = self.data.get('materials', [])

        current_materials = OffersMaterial.objects.filter(offer_id=offer.id)

        if current_materials:
            excluded_materials = current_materials.exclude(material_id__in=materials)

            for material in excluded_materials:
                material.delete()

            current_ids = [material.material_id for material in current_materials]
            materials = [material for material in materials if int(material) not in current_ids]

        for material in materials:
            OffersMaterial.objects.create(offer_id=offer.id, material_id=material)

    def save(self, commit=True):
        """Save form"""

        title = self.data['title']
        self.instance.title_es = title.es
        self.instance.title_en = title.en

        if 'description' in self.data:
            self.instance.description_es = self.data['description'].es
            self.instance.description_en = self.data['description'].en

        offer = super(AdminCreateOfferForm, self).save(commit=commit)

        self.clean_images(offer)
        self.clean_materials(offer)

        return offer


class AdminUpdateOfferForm(AdminCreateOfferForm):
    """
    Form to update an offer from admin
    """

    def __init__(self, *args, **kwargs):
        super(AdminUpdateOfferForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False

    class Meta:
        """Meta class"""
        model = Offer
        fields = ['subcategory', 'currency', 'price', 'recommended']


class AdminControlOfferForm(ModelForm):
    """
    Form to control an offer from admin
    """

    class Meta:
        """Meta class"""
        model = Offer
        fields = []

    def activate(self, activate):
        """Activate offer"""

        self.instance.on_sale = activate
        self.instance.save()

    def recommend(self, recommend):
        """Recommend offer"""

        self.instance.recommended = recommend
        self.instance.save()

    def delete(self):
        """Delete offer"""

        images = Image.objects.filter(offer_id=self.instance.id)
        for image in images:
            Image.remove(public_id=image.public_id)

        self.instance.delete()


class AdminCreateMaterialForm(ModelForm):
    """
    Form to create a material from admin
    """

    class Meta:
        """Meta class"""
        model = Material
        fields = []

    def save(self, commit=True):
        """Save form"""
        title = self.data['title']
        self.instance.title_es = title.es
        self.instance.title_en = title.en

        return super(AdminCreateMaterialForm, self).save(commit=commit)


class AdminUpdateMaterialForm(AdminCreateMaterialForm):
    """
    Form to update a material from admin
    """

    def __init__(self, *args, **kwargs):
        super(AdminUpdateMaterialForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False

    class Meta:
        """Meta class"""
        model = Material
        fields = []


class AdminDeleteMaterialForm(ModelForm):
    """
    Form to delete a material from admin
    """

    class Meta:
        """Meta class"""
        model = Material
        fields = []

    def delete(self):
        """Delete material"""

        self.instance.delete()
