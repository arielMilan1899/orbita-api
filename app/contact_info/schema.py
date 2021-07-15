"""Schema for contact_info app"""
import graphene
from graphene_django import DjangoObjectType
from contact_info.models import ContactInfo, Manufacturer, Message


class ContactInfoType(DjangoObjectType):
    """Type for ContactInfo model"""

    class Meta:
        """Meta Class"""
        model = ContactInfo
        fields = (
            'id', 'email', 'phone', 'address', 'twitter', 'facebook', 'linkedIn', 'about', 'pdf_url', 'pdf_public_id')
        use_connection = True


class ManufacturerType(DjangoObjectType):
    """Type for Manufacturer model"""

    class Meta:
        """Meta Class"""
        model = Manufacturer
        fields = ('id', 'name', 'logo_url', 'logo_public_id')
        use_connection = True


class CreateMessageMutation(graphene.Mutation):
    """Mutation to create a message"""

    class Input:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        topic = graphene.String(required=True)
        message = graphene.String(required=False)

    ok = graphene.Boolean()

    def mutate(self, info, name, email, topic, message=''):
        Message.objects.create(name=name, email=email, topic=topic, message=message)
        return CreateMessageMutation(ok=True)


class ContactInfoQuery:
    """Schema queries"""
    contact_info = graphene.Field(ContactInfoType, description='Return the contact info')
    manufacturers = graphene.List(ManufacturerType, description='Return a list of manufacturers')

    @classmethod
    def resolve_contact_info(cls, instance, info):
        """Resolve the contact info"""

        return ContactInfo.objects.last()

    @classmethod
    def resolve_manufacturers(cls, instance, info):
        """Resolve the manufacturers"""

        return Manufacturer.objects.all()


class ContactInfoMutation:
    """Schema mutations"""
    create_message = CreateMessageMutation.Field(description='Create a new message')
