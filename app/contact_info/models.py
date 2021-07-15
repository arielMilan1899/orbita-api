from django.db import models
from django_mysql.models import EnumField
from djchoices import DjangoChoices, ChoiceItem


class ContactInfo(models.Model):
    """Model for site contact info"""

    email = models.EmailField(null=True, blank=True, help_text='Email field')
    phone = models.CharField(max_length=50, blank=True, null=True, help_text='Phone field')
    address = models.CharField(max_length=300, blank=True, null=True, help_text='Address field')
    twitter = models.CharField(max_length=300, blank=True, null=True, help_text='Twitter account')
    facebook = models.CharField(max_length=300, blank=True, null=True, help_text='Facebook account')
    linkedIn = models.CharField(max_length=300, blank=True, null=True, help_text='LinkedId account')
    about = models.TextField(blank=True, null=True, help_text='About us')
    pdf_url = models.CharField(max_length=150, blank=True, null=True, help_text='Pdf url')
    pdf_public_id = models.CharField(max_length=150, blank=True, null=True, help_text='Pdf public_id')


class Message(models.Model):
    """Model for clients messages"""

    class StatusChoices(DjangoChoices):
        """
        State for messages
        """
        unread = ChoiceItem('UNREAD', 'This message has not been read')
        read = ChoiceItem('READ', 'This message has been read')

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300, help_text='Name field')
    email = models.EmailField(help_text='Email field')
    topic = models.CharField(max_length=300, help_text='Phone field')
    message = models.TextField(blank=True, null=True, help_text='Message')
    status = EnumField(choices=StatusChoices.choices, default=StatusChoices.unread, help_text='Message status')


class Manufacturer(models.Model):
    """Model for site manufacturers"""
    name = models.CharField(max_length=300, blank=True, null=True, help_text='Name field')
    logo_url = models.CharField(max_length=150, blank=True, null=True, help_text='Image url')
    logo_public_id = models.CharField(max_length=150, blank=True, null=True, help_text='Image public_id')
