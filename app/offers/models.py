from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django_mysql.models import EnumField
from djchoices import DjangoChoices, ChoiceItem
from cloudinary import api as cloudinary_api


class Category(models.Model):
    """Offer's categories model. Each offer belongs to a category"""

    title_es = models.CharField(max_length=63, help_text='Category spanish title')
    title_en = models.CharField(max_length=63, help_text='Category english title')
    description_es = models.CharField(max_length=250, blank=True, null=True, help_text='Category spanish description')
    description_en = models.CharField(max_length=250, blank=True, null=True, help_text='Category english description')
    slug_es = models.SlugField(max_length=65, unique=True, help_text='Category spanish slug')
    slug_en = models.SlugField(max_length=65, unique=True, help_text='Category english slug')
    order = models.IntegerField(default=0, help_text='Order of visualization')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, unique=False, null=True,
                                        help_text='Category parent')
    poster_url = models.CharField(max_length=150, blank=True, null=True, help_text='Image url')
    poster_public_id = models.CharField(max_length=150, blank=True, null=True, help_text='Image public_id')

    # pylint: disable=W1113,W0221
    def save(self, *args, **kwargs):
        """Create Category"""
        self.generate_slug()

        super(Category, self).save(*args, **kwargs)

    def generate_slug(self):
        """
        Generate a unique slug
        """
        unique_slug_es = slugify(self.title_es)
        unique_slug_en = slugify(self.title_en)

        if self.parent_category:
            slug_es = "%s_%s" % (self.parent_category.slug_es, unique_slug_es)
            slug_en = "%s_%s" % (self.parent_category.slug_en, unique_slug_en)
        else:
            slug_es = unique_slug_es
            slug_en = unique_slug_en

        self.slug_es = slug_es
        self.slug_en = slug_en


class Offer(models.Model):
    """Offer definition"""

    class SortChoices(DjangoChoices):
        """
        Choices for sort results
        """
        price = ChoiceItem("price", 'Sort by price')
        created_on = ChoiceItem("created_on", 'Sort by created_on')
        updated_on = ChoiceItem("updated_on", 'sort by updated_on')

    class CurrencyChoices(DjangoChoices):
        """
        Type of currency
        """
        cuc = ChoiceItem('CUC', 'Cuban Convertible Peso')
        usd = ChoiceItem('USD', 'US Dollar')
        cup = ChoiceItem('CUP', 'Cuban Peso')

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    on_sale = models.BooleanField(default=True, help_text='Offer is on sale')
    title_es = models.CharField(max_length=120, help_text='Offer title')
    title_en = models.CharField(max_length=120, help_text='Offer title')
    description_es = models.TextField(blank=True, null=True, help_text='Offer description')
    description_en = models.TextField(blank=True, null=True, help_text='Offer description')
    price = models.FloatField(null=True, blank=True, help_text='Offer price')
    currency = EnumField(choices=CurrencyChoices.choices, default=CurrencyChoices.cuc, null=True, blank=True,
                         help_text='Currency type')
    slug_es = models.SlugField(max_length=150, unique=True, null=True, default=None, help_text='Offer slug')
    slug_en = models.SlugField(max_length=150, unique=True, null=True, default=None, help_text='Offer slug')
    permalink_es = models.CharField(max_length=200, unique=True, null=True, default=None, help_text='Offer permalink')
    permalink_en = models.CharField(max_length=200, unique=True, null=True, default=None, help_text='Offer permalink')
    short_description_es = models.CharField(max_length=settings.OFFER_SHORT_DESCRIPTION_MAX_LENGTH, blank=True,
                                            null=True, help_text='Offer short description')
    short_description_en = models.CharField(max_length=settings.OFFER_SHORT_DESCRIPTION_MAX_LENGTH, blank=True,
                                            null=True, help_text='Offer short description')
    subcategory = models.ForeignKey(Category, help_text='Related category', on_delete=models.CASCADE)
    recommended = models.BooleanField(default=False, help_text='Offer is recommended')

    # pylint: disable=W1113,W0221
    def save(self, *args, **kwargs):
        """Create Offer"""

        self.generate_short_description()

        # set currency to None if price is None
        if self.price is None:
            self.currency = None

        super(Offer, self).save(*args, **kwargs)

        self.generate_slug_and_permalink()

        super(Offer, self).save()

    def generate_slug_and_permalink(self):
        """
        Generate a unique slug and unique permalink
        """
        unique_title_es = "{slug}-{id}".format(slug=self.title_es, id=self.id)
        unique_title_en = "{slug}-{id}".format(slug=self.title_en, id=self.id)
        unique_slug_es = slugify(unique_title_es)
        unique_slug_en = slugify(unique_title_en)
        category_data_es = self.subcategory.slug_es.split('_')
        category_data_en = self.subcategory.slug_en.split('_')
        permalink_es = '/{parent_category_slug}/{subcategory_slug}/{offer_slug}.html'.format(
            parent_category_slug=category_data_es[0],
            subcategory_slug=category_data_es[1],
            offer_slug=unique_slug_es
        )
        permalink_en = '/{parent_category_slug}/{subcategory_slug}/{offer_slug}.html'.format(
            parent_category_slug=category_data_en[0],
            subcategory_slug=category_data_en[1],
            offer_slug=unique_slug_en
        )

        self.slug_es = unique_slug_es
        self.slug_en = unique_slug_en
        self.permalink_es = permalink_es
        self.permalink_en = permalink_en

    def generate_short_description(self):
        """
        Generate offer short_description
        """
        if self.description_es:
            words = self.description_es.split(' ')
            short_description = ''
            for word in words:
                result = short_description + word
                if len(result) > settings.OFFER_SHORT_DESCRIPTION_MAX_LENGTH:
                    break
                short_description += word + ' '
            self.short_description_es = short_description.rstrip()

        if self.description_en:
            words = self.description_en.split(' ')
            short_description = ''
            for word in words:
                result = short_description + word
                if len(result) > settings.OFFER_SHORT_DESCRIPTION_MAX_LENGTH:
                    break
                short_description += word + ' '
            self.short_description_en = short_description.rstrip()


class Image(models.Model):
    """Offer's images model"""

    url = models.CharField(max_length=150, help_text='Image url')
    public_id = models.CharField(max_length=150, help_text='Image public_id')
    offer = models.ForeignKey(Offer, help_text='Related offer', on_delete=models.CASCADE)

    @staticmethod
    def remove(public_id):
        """Remove image from storage"""

        if public_id:
            cloudinary_api.delete_resources(public_id)


class Material(models.Model):
    """Material model"""

    title_es = models.CharField(max_length=120, unique=True, help_text='Material title')
    title_en = models.CharField(max_length=120, unique=True, help_text='Material title')


class OffersMaterial(models.Model):
    """Offer`s materials"""

    offer = models.ForeignKey(Offer, help_text='Related offer', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, help_text='Related material', on_delete=models.CASCADE)

    class Meta:
        """Model meta-class data"""
        unique_together = ('offer', 'material')
