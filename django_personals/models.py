from django.db import models
from django.utils import translation
from .abstracts import ContactAbstract, AddressAbstract, PersonAbstract

_ = translation.gettext_lazy


class Person(PersonAbstract):
    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')