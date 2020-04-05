import enum
import uuid
from django.db import models, transaction
from django.utils import translation, timezone, text
from django.utils.functional import cached_property
from django.conf import settings
from django.contrib.auth import get_user_model


_ = translation.gettext_lazy

class MaxLength(enum.Enum):
    SHORT = 128
    MEDIUM = 256
    LONG = 512
    XLONG = 1024
    TEXT = 2048
    RICHTEXT = 10000

class Gender(enum.Enum):
    MALE = 'M'
    FEMALE = 'F'


class BaseManager(models.Manager):
    """
        Implement paranoid mechanism queryset
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get(self, *args, **kwargs):
        kwargs['is_deleted'] = False
        return super().get(*args, **kwargs)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    objects = BaseManager()

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    is_deleted = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_('is deleted?'))
    deleted_by = models.ForeignKey(
        get_user_model(),
        editable=False,
        null=True, blank=True,
        related_name="%(class)s_deleter",
        on_delete=models.CASCADE,
        verbose_name=_('deleter'))
    deleted_at = models.DateTimeField(
        null=True, blank=True, editable=False)
    created_at = models.DateTimeField(
        default=timezone.now, editable=False)
    modified_at = models.DateTimeField(
        null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super().save(**kwargs)

    def delete(self, using=None, keep_parents=False, paranoid=False):
        """
            Give paranoid delete mechanism to each record
        """
        if paranoid:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

class ContactInfo(models.Model):
    class Meta:
        abstract = True

    phone = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('Phone'))
    fax = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('Fax'))
    whatsapp = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('Whatsapp'))
    email = models.EmailField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('Email'))
    website = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('Website'))


class Address(models.Model):
    class Meta:
        abstract = True

    street = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.LONG.value,
        verbose_name=_('Street'))
    city = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('City'))
    province = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('Province'))
    country = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('Country'))
    zipcode = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('Zip Code'))

    def __str__(self):
        return self.street

    @property
    def fulladdress(self):
        address = [self.street, self.city, self.province, self.country, self.zipcode]
        return ", ".join(map(str, address))


class PersonManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_employees(self):
        return self.filter(employee__isnull=False)

    def get_partners(self):
        return self.filter(partners__isnull=False)


class Person(BaseModel):
    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        permissions = (
            ('export_person', 'Can export Person'),
            ('import_person', 'Can import Person'),
            ('change_status_person', 'Can change status Person')
        )

    objects = PersonManager()

    show_title = models.BooleanField(
        default=False,
        verbose_name=_('Show title'),
        help_text=_('Show Mr or Mrs in front of name'))
    show_name_only = models.BooleanField(
        default=False,
        verbose_name=_('Show name only'),
        help_text=_('Show name only without academic title'))
    title = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Title"))
    fullname = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Full name"))
    nickname = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Nick name"))
    front_title = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Front title"),
        help_text=_("Academic title prefix, eg: Dr or Prof. Dr"))
    back_title = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Back title"),
        help_text=_("Academic title suffix, eg: Phd"))
    gender = models.CharField(
        max_length=1,
        choices=[(str(x.value), str(x.name)) for x in Gender],
        default=Gender.MALE.value,
        verbose_name=_('Gender'))
    religion = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('Religion'))
    nation = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('Nation'))
    date_of_birth = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('Date of birth'))
    place_of_birth = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('Place of birth'))

    account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name='person',
        on_delete=models.CASCADE,
        verbose_name=_('User account'))

    is_employee_applicant = models.BooleanField(
        default=False, verbose_name=_('Employee applicant'))
    is_partner_applicant = models.BooleanField(
        default=False, verbose_name=_('Partner applicant'))

    @cached_property
    def fullname_with_title(self):
        name = []
        if self.title and self.show_title:
            name.append(self.title)
        if self.front_title and not self.show_name_only:
            name.append(str(self.front_title) + '.')
        if self.fullname:
            name.append(self.fullname)
        if self.back_title and not self.show_name_only:
            name.append(', ' + str(self.back_title))
        return " ".join(name)

    def __str__(self):
        return str(self.fullname_with_title)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @cached_property
    def is_user(self):
        user = self.user_account
        return bool(user)

    def create_user_account(self, username=None, password=None):
        if not self.user_account:
            with transaction.atomic():
                usermodel = settings.AUTH_USER_MODEL
                username = username if username else text.slugify(
                    self.fullname)
                password = password if password else 'default_pwd'
                new_user = usermodel.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=False
                )
                self.user_account = new_user
                self.save()

    def bind_user_account(self, user):
        with transaction.atomic():
            self.user_account = user
            self.save()


class PersonContact(ContactInfo, BaseModel):
    class Meta:
        verbose_name = _('Person Contact')
        verbose_name_plural = _('Person Contacts')

    person = models.OneToOneField(
        Person, on_delete=models.CASCADE,
        related_name='contact',
        verbose_name=_("Person"))

    # Social Media
    facebook = models.URLField(
        null=True, blank=True,
        help_text=_('Facebook page URL'))
    twitter = models.CharField(
        null=True, blank=True,
        max_length=255,
        help_text=_('twitter username, without the @'))
    instagram = models.CharField(
        null=True, blank=True,
        max_length=255,
        help_text=_('Instagram username, without the @'))
    youtube = models.URLField(
        null=True, blank=True,
        help_text=_('YouTube channel or user account URL'))


class PersonAddress(Address, BaseModel):
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Address')

    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_("Person"))
    is_primary = models.BooleanField(
        default=True, verbose_name=_('Primary'))
    name = models.CharField(
        null=True, blank=False,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Name"), help_text=_('E.g. Home Address or Office Address'))