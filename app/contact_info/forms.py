"""Forms for contact_info app"""
from django.forms import ModelForm
from contact_info.models import ContactInfo, Manufacturer, Message
from offers.models import Image


class AdminUpdateContactInfoForm(ModelForm):
    """
    Form to update the contact info
    """

    class Meta:
        """Meta class"""
        model = ContactInfo
        fields = ['email', 'phone', 'address', 'facebook', 'linkedIn', 'twitter', 'about', 'pdf_url', 'pdf_public_id']

    def __init__(self, *args, **kwargs):
        super(AdminUpdateContactInfoForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False

    def clean(self):

        cleaned_data = super(AdminUpdateContactInfoForm, self).clean()

        if self.instance.pdf_public_id != self.cleaned_data.get('pdf_public_id', None):
            Image.remove(self.instance.pdf_public_id)

        return cleaned_data


class AdminCreateManufacturerForm(ModelForm):
    """
    Form to create a manufacturer
    """

    class Meta:
        """Meta class"""
        model = Manufacturer
        fields = ['name', 'logo_public_id', 'logo_url']


class AdminUpdateManufacturerForm(AdminCreateManufacturerForm):
    """
    Form to update a manufacturer
    """

    def __init__(self, *args, **kwargs):
        super(AdminUpdateManufacturerForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False

    class Meta:
        """Meta class"""
        model = Manufacturer
        fields = ['name', 'logo_public_id', 'logo_url']

    def clean(self):

        cleaned_data = super(AdminUpdateManufacturerForm, self).clean()

        if self.instance.logo_public_id != self.cleaned_data.get('logo_public_id', None):
            Image.remove(self.instance.logo_public_id)

        return cleaned_data


class AdminDeleteManufacturerForm(ModelForm):
    """
    Form to delete a manufacturer
    """

    class Meta:
        """Meta class"""
        model = Manufacturer
        fields = []

    def delete(self):
        """Delete manufacturer"""
        Image.remove(self.instance.logo_public_id)
        self.instance.delete()


class AdminDeleteMessageForm(ModelForm):
    """
    Form to delete a message
    """

    class Meta:
        """Meta class"""
        model = Message
        fields = []

    def delete(self):
        """Delete message"""
        self.instance.delete()
