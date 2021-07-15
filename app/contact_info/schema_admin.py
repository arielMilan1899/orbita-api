"""Schema admin for contact_info app"""
from graphene import Field, Int, List
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from accounts.mixins import LoginRequiredMutation
from api.utils.schema import BulkDjangoFormMutation, EditDjangoModelFormMutation
from contact_info.forms import AdminUpdateContactInfoForm, AdminCreateManufacturerForm, AdminUpdateManufacturerForm, \
    AdminDeleteManufacturerForm, AdminDeleteMessageForm
from contact_info.models import ContactInfo, Manufacturer, Message
from contact_info.schema import ContactInfoType, ManufacturerType


class AdminUpdateContactInfoMutation(LoginRequiredMutation, EditDjangoModelFormMutation):
    """
    Mutation to update the contact info
    """
    contact_info = Field(ContactInfoType, description='ContactInfo instance')

    class Meta:
        """Meta Class"""
        model = ContactInfo
        form_class = AdminUpdateContactInfoForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateContactInfoForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        contact_info = form.save()
        return cls(contact_info=contact_info)


class AdminCreateManufacturerMutation(LoginRequiredMutation, DjangoModelFormMutation):
    """
    Mutation to create a manufacturer
    """
    manufacturer = Field(ManufacturerType, description='Manufacturer instance')

    class Meta:
        """Meta Class"""
        model = Manufacturer
        form_class = AdminCreateManufacturerForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminCreateManufacturerForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        manufacturer = form.save()
        return cls(manufacturer=manufacturer)


class AdminUpdateManufacturerMutation(LoginRequiredMutation, EditDjangoModelFormMutation):
    """
    Mutation to update a manufacturer
    """
    manufacturer = Field(ManufacturerType, description='Manufacturer instance')

    class Meta:
        """Meta Class"""
        model = Manufacturer
        form_class = AdminUpdateManufacturerForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminUpdateManufacturerForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        manufacturer = form.save()
        return cls(manufacturer=manufacturer)


class AdminDeleteManufacturerMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to delete a manufacturer"""

    class Meta:
        """Meta Class"""
        model = Manufacturer
        form_class = AdminDeleteManufacturerForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminDeleteManufacturerForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        manufacturer_id = form.instance.id
        form.delete()
        return manufacturer_id


class MessageType(DjangoObjectType):
    """Type for Message model"""

    class Meta:
        """Meta Class"""
        model = Message
        fields = ('id', 'created_on', 'name', 'email', 'topic', 'message', 'status')
        use_connection = True


class AdminDeleteMessageMutation(LoginRequiredMutation, BulkDjangoFormMutation):
    """Mutation to delete a message"""

    class Meta:
        """Meta Class"""
        model = Message
        form_class = AdminDeleteMessageForm

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :type form: AdminDeleteMessageForm
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        message_id = form.instance.id
        form.delete()
        return message_id


class AdminMessageQuery:
    """
    Root class of the message model queries
    """
    messages = List(MessageType, description='Return a list of messages')
    message = Field(MessageType, id=Int(required=True), description='Return a message instance')

    @classmethod
    def resolve_messages(cls, instance, info):
        """
        Resolve all messages
        :param instance: Query instance
        :param info: Schema info
        :return: All messages
        """
        return Message.objects.all().order_by('-created_on')

    @classmethod
    def resolve_message(cls, instance, info, id, **kwargs):
        """
        Resolve single message using id or slug.
        :param instance: Query instance
        :param info: Schema info
        :return: MessageType node of Message model.
        """
        message = Message.objects.get(id=id)

        if message.status == Message.StatusChoices.unread:
            message.status = Message.StatusChoices.read
            message.save()

        return message


class AdminContactInfoMutation:
    """
    Root Class of the contact info app mutations
    """
    update_contact_info = AdminUpdateContactInfoMutation.Field(description='Update the contact info.')
    create_manufacturer = AdminCreateManufacturerMutation.Field(description='Create a manufacturer.')
    update_manufacturer = AdminUpdateManufacturerMutation.Field(description='Update a manufacturer.')
    delete_manufacturer = AdminDeleteManufacturerMutation.Field(description='Delete a manufacturer.')
    delete_message = AdminDeleteMessageMutation.Field(description='Delete a message.')
