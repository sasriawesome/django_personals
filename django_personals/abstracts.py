import enum
import uuid
from django.db import models, transaction
from django.utils import translation, timezone, text
from django.utils.functional import cached_property
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
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


class EducationStatus(enum.Enum):
    FINISHED = 'FNS'
    ONGOING = 'ONG'
    UNFINISHED = 'UNF'


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

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')


class ParanoidModel(models.Model):
    class Meta:
        abstract = True

    objects = BaseManager()

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


class ContactAbstract(models.Model):
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


class SocialAbstract(models.Model):
    class Meta:
        abstract = True

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


class AddressAbstract(models.Model):
    class Meta:
        abstract = True

    is_primary = models.BooleanField(
        default=True, verbose_name=_('Primary'))
    name = models.CharField(
        null=True, blank=False,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Name"),
        help_text=_('E.g. Home Address or Office Address'))
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


class TitleMixin(models.Model):
    class Meta:
        abstract = True

    fullname = NotImplemented
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


class PersonAbstract(models.Model):
    class Meta:
        abstract = True

    fullname = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Full name"))
    nickname = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Nick name"))

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

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @cached_property
    def is_user(self):
        user = self.account
        return bool(user)


class HistoryBase(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name'))
    institution = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Institution"))
    date_start = models.DateField(
        default=timezone.now,
        verbose_name=_("Date start"))
    date_end = models.DateField(
        default=timezone.now,
        verbose_name=_("Date end"))
    status = models.CharField(
        max_length=5,
        default=EducationStatus.ONGOING.value,
        choices=[(str(x.value), str(x.name)) for x in EducationStatus],
        verbose_name=_("Current status"))

    def __str__(self):
        return self.name


class FormalEduAbstract(HistoryBase):
    class Meta:
        abstract = True

    major = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("Major"),
        help_text=_("ex: Information System or Accounting"))


class NonFormalEduAbstract(HistoryBase):
    class Meta:
        abstract = True

    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("Description"))


class WorkingAbstract(HistoryBase):
    class Meta:
        abstract = True

    CONTRACT = 'CTR'
    FIXED = 'FXD'
    OUTSOURCE = 'OSR'
    ELSE = 'ELS'
    STATUS = (
        (CONTRACT, _("Contract")),
        (FIXED, _("Fixed")),
        (OUTSOURCE, _("Outsource")),
        (ELSE, _("Else"))
    )

    department = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Department"))
    position = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Position"))
    description = models.TextField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Description"))
    employment = models.CharField(
        max_length=5, default=CONTRACT, choices=STATUS,
        verbose_name=_("Employment"))

    def __str__(self):
        return "%s, %s" % (self.institution, self.position)


class VolunteerAbstract(models.Model):
    class Meta:
        abstract = True

    ACTIVE = 'ACT'
    INACTIVE = 'INC'
    STATUS = (
        (ACTIVE, _("Active")),
        (INACTIVE, _("Inactive")),
    )

    organization = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Organization"))
    position = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Position"))
    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Description"))
    date_start = models.DateField(
        default=timezone.now, verbose_name=_("Date start"))
    date_end = models.DateField(
        default=timezone.now, verbose_name=_("Date end"))
    status = models.CharField(
        max_length=5, default=ACTIVE, choices=STATUS,
        verbose_name=_("Status"))

    def __str__(self):
        return "%s, %s" % (self.organization, self.position)


class AwardAbstract(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Name"))
    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("Description"))
    date = models.DateTimeField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('Created date'))

    def __str__(self):
        return self.name


class SkillAbstract(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Name"))
    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("Description"))
    level = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ],
        verbose_name=_('Skill level'))

    def __str__(self):
        return self.name


class PublicationAbstract(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Title"))
    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("Description"))
    publisher = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("Publisher"))
    date_published = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('Published date'))
    permalink = models.URLField(
        null=True, blank=True,
        verbose_name=_('URL'))

    def __str__(self):
        return self.title


class FamilyAbstract(models.Model):
    class Meta:
        abstract = True

    FATHER = '1'
    MOTHER = '2'
    SIBLING = '3'
    CHILD = '4'
    HUSBAND = '5'
    WIFE = '6'
    OTHER = '99'
    RELATION = (
        (FATHER, _('Father')),
        (MOTHER, _('Mother')),
        (SIBLING, _('Sibling')),
        (CHILD, _('Children')),
        (HUSBAND, _('Husband')),
        (WIFE, _('Wife')),
        (OTHER, _('Other')),
    )

    relation = models.CharField(
        choices=RELATION, default=OTHER,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("relation"))
    relationship = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Relationship"))
    name = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Name"))
    date_of_birth = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('Date of birth'))
    place_of_birth = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('Place of birth'))
    job = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("Job"))
    address = models.TextField(
        max_length=MaxLength.LONG.value,
        null=True, blank=True,
        verbose_name=_("Address"))

    def __str__(self):
        return self.name
