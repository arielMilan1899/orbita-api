# -*- coding: utf-8 -*-
"""
Helpers to Graphql schemas
"""
from __future__ import unicode_literals

from collections import OrderedDict

from django.forms import model_to_dict
from graphene import Enum, List, ID, Field, InputField
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.converter import get_choices
from graphene_django.forms.mutation import BaseDjangoFormMutation, DjangoFormMutationOptions, DjangoModelFormMutation
from graphene_django.types import ErrorType

from api.utils.exceptions import BaseError


def django_choice_to_type(type_name, django_choices):
    """
    Return an emun type from a DjangoChoices class
    :param type_name: Type name to output
    :param django_choices: input DjangoChoices class
    :return: enum
    """
    choices = list(get_choices(django_choices.choices))
    named_choices = [(c[0], c[1]) for c in choices]

    enum = Enum(
        type_name,
        named_choices,
        description=lambda a: django_choices.get_choice(a.value).label if a else type_name
    )
    return enum


def load_model_prev_data(kwargs):
    """
    Load model data from db
    :param kwargs:
    :return: filled kwargs
    """
    if 'instance' in kwargs:
        model_data = model_to_dict(kwargs['instance'])
        model_data.update(kwargs['data'])
        kwargs['data'] = model_data

    return kwargs


class EditDjangoModelFormMutation(DjangoModelFormMutation):
    """
    Extends DjangoFormMutation to initialize the form and its fields.
    """

    class Meta:
        """Meta class"""
        abstract = True

    errors = List(ErrorType)

    @classmethod
    def get_form_kwargs(cls, root, info, **input_fields):
        """Override parent to get the user in request"""
        kwargs = super(EditDjangoModelFormMutation, cls).get_form_kwargs(root, info, **input_fields)
        return load_model_prev_data(kwargs)


class BulkDjangoFormMutation(BaseDjangoFormMutation):
    """
    Extends BaseDjangoFormMutation to handle multiple ids.
     It creates one form instance for each id
    """

    class Meta:
        """Meta class"""
        abstract = True

    success_ids = List(ID, description='Ids of successfully mutates')
    errors = List(ErrorType)

    # pylint: disable=W0221
    @classmethod
    def __init_subclass_with_meta__(cls, form_class=None, model=None,
                                    only_fields=(), exclude_fields=(), **options):
        if not form_class:
            raise Exception('form_class is required for BulkDjangoFormMutation')

        if not model:
            model = form_class._meta.model

        if not model:
            raise Exception("model is required for BulkDjangoFormMutation")

        input_fields = {"ids": List(ID, required=True, description='list of ids to mutate')}
        output_fields = OrderedDict()

        _meta = DjangoFormMutationOptions(cls)
        _meta.form_class = form_class
        _meta.fields = yank_fields_from_attrs(
            output_fields,
            _as=Field,
        )
        _meta.model = model

        input_fields = yank_fields_from_attrs(
            input_fields,
            _as=InputField,
        )
        super(BulkDjangoFormMutation, cls).__init_subclass_with_meta__(_meta=_meta,
                                                                       input_fields=input_fields,
                                                                       **options)

    # pylint: disable=W0622
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        pks = input.pop("ids", None)
        errors = []
        success_ids = []

        # pylint: disable=C0103
        for pk in pks:
            input['id'] = pk
            try:
                form = cls.get_form(root, info, **input)

                if form.is_valid():
                    success_id = cls.safe_perform_mutate(form, info)
                    if isinstance(success_id, (int,)):
                        success_ids.append(success_id)
                else:
                    for key, value in form.errors.items():
                        errors.append(ErrorType(field=key, messages=value))

            except cls._meta.model.DoesNotExist:
                pass

        if errors:
            return cls(success_ids=success_ids, errors=errors)

        return cls(success_ids=success_ids)

    @classmethod
    def get_form_kwargs(cls, root, info, **input_fields):
        """Override parent to get the user in request"""
        kwargs = super(BulkDjangoFormMutation, cls).get_form_kwargs(root, info, **input_fields)
        return load_model_prev_data(kwargs)

    @classmethod
    def safe_perform_mutate(cls, form, info):
        """
        Catch any base error from perform mutate and return None
        """
        try:
            result = cls.perform_mutate(form, info)
            return result
        except BaseError:
            return None
