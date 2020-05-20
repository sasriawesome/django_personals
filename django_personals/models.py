import uuid
from django.db import models
from django.utils import translation, timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from .enums import MaxLength, ActiveStatus, PrivacyStatus
from django_personals.enums import (
    Gender, EducationStatus, WorkingStatus, FamilyRelation, AddressName
)

_ = translation.gettext_lazy


class BaseManager(models.Manager):
    """
        Implement paranoid mechanism queryset
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_trash=False)

    def get(self, *args, **kwargs):
        kwargs['is_trash'] = False
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
    is_trash = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_('trash'))
    trashed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        null=True, blank=True,
        related_name="%(class)s_trashes",
        on_delete=models.CASCADE,
        verbose_name=_('trashed by'))
    trashed_at = models.DateTimeField(
        null=True, blank=True, editable=False)

    def pass_delete_validation(self):
        return True

    def get_deletion_error_message(self):
        return _("E1001: %s deletion can't be performed.") % self._meta.verbose_name

    def get_deletion_message(self):
        return _("E1010: %s deletion can't be performed.") % self._meta.verbose_name

    def delete(self, using=None, keep_parents=False, paranoid=False, user=None):
        """
            Give paranoid delete mechanism to each record
        """
        if not self.pass_delete_validation():
            raise ValidationError(self.get_deletion_error_message())

        if paranoid:
            self.is_trash = True
            self.trashed_by = user
            self.trashed_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def pass_restore_validation(self):
        return self.is_trash

    def get_restoration_error_message(self):
        return _("E1002: %s restoration can't be performed.") % self._meta.verbose_name

    def restore(self):
        if not self.pass_restore_validation():
            raise ValidationError(self.get_restoration_error_message())

        self.is_trash = False
        self.trashed_by = None
        self.trashed_at = None
        self.save()


class ContactAbstract(models.Model):
    class Meta:
        abstract = True

    phone = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('phone'))
    fax = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('fax'))
    email = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('email'),
        help_text=_('your public email'))
    whatsapp = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('whatsapp'))
    website = models.CharField(
        max_length=MaxLength.SHORT.value,
        null=True, blank=True,
        verbose_name=_('website'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))


class SocialAbstract(models.Model):
    class Meta:
        abstract = True

    # Social Media
    facebook = models.SlugField(
        null=True, blank=True,
        help_text=_('Facebook page or name'))
    twitter = models.SlugField(
        null=True, blank=True,
        max_length=255,
        help_text=_('Twitter username, without the @'))
    instagram = models.SlugField(
        null=True, blank=True,
        max_length=255,
        help_text=_('Instagram username, without the @'))
    youtube = models.SlugField(
        null=True, blank=True,
        help_text=_('Youtube channel name.'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))


class AddressAbstract(models.Model):
    class Meta:
        abstract = True

    is_primary = models.BooleanField(
        default=True, verbose_name=_('primary'))
    name = models.CharField(
        null=True, blank=False,
        max_length=MaxLength.MEDIUM.value,
        choices=AddressName.CHOICES.value,
        default=AddressName.HOME.value,
        verbose_name=_("name"),
        help_text=_('E.g. Home Address or Office Address'))
    street = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.LONG.value,
        verbose_name=_('street'))
    city = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('city'))
    province = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('province'))
    country = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('country'))
    zipcode = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_('zip code'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))

    def __str__(self):
        return self.street

    @property
    def fulladdress(self):
        address = [self.street, self.city, self.province, self.country, self.zipcode]
        return ", ".join(map(str, address))


class TitleMixin(models.Model):
    class Meta:
        abstract = True

    show_title = models.BooleanField(
        default=False,
        verbose_name=_('show title'),
        help_text=_('Show Mr or Mrs in front of name'))
    show_academic_title = models.BooleanField(
        default=False,
        verbose_name=_('Show academic title'),
        help_text=_('Show name with academic title'))
    title = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("title"))
    front_title = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("front title"),
        help_text=_("Front academic title."))
    back_title = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("back title"),
        help_text=_("Back academic title."))


class PersonMinimalAbstract(BaseModel):
    class Meta:
        abstract = True

    pid = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("PID"),
        help_text=_('Personal Identifier Number'))
    gender = models.CharField(
        max_length=1,
        choices=Gender.CHOICES.value,
        default=Gender.MALE.value,
        verbose_name=_('gender'))
    date_of_birth = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('date of birth'))
    place_of_birth = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('place of birth'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))


class PersonAbstract(PersonMinimalAbstract):
    class Meta:
        abstract = True

    nickname = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("nick name"))
    about_me = models.TextField(
        null=True, blank=True,
        max_length=MaxLength.SHORT.value,
        verbose_name=_("about me"))
    religion = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('religion'))
    nation = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('nation'))


class HistoryBase(BaseModel):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=50,
        verbose_name=_('name'))
    institution = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("institution"))
    date_start = models.DateField(
        default=timezone.now,
        verbose_name=_("date start"))
    date_end = models.DateField(
        default=timezone.now,
        verbose_name=_("date end"))
    document_link = models.URLField(
        null=True, blank=True,
        verbose_name=_('document link'),
        help_text=_('Provide support document link'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))


class FormalEduAbstract(HistoryBase):
    class Meta:
        abstract = True

    name = None
    major = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("major"),
        help_text=_("ex: Information System or Accounting"))
    status = models.CharField(
        max_length=5,
        default=EducationStatus.ONGOING.value,
        choices=EducationStatus.CHOICES.value,
        verbose_name=_("current status"))


class NonFormalEduAbstract(HistoryBase):
    class Meta:
        abstract = True

    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("description"))
    status = models.CharField(
        max_length=5,
        default=EducationStatus.ONGOING.value,
        choices=EducationStatus.CHOICES.value,
        verbose_name=_("current status"))


class WorkingAbstract(HistoryBase):
    class Meta:
        abstract = True

    department = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("department"))
    position = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("position"))
    description = models.TextField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("description"))
    employment = models.CharField(
        max_length=5,
        default=WorkingStatus.CONTRACT.value,
        choices=WorkingStatus.CHOICES.value,
        verbose_name=_("employment"))

    def __str__(self):
        return "%s, %s" % (self.institution, self.position)


class VolunteerAbstract(BaseModel):
    class Meta:
        abstract = True

    organization = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("organization"))
    position = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("position"))
    description = models.TextField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("description"))
    date_start = models.DateField(
        default=timezone.now,
        verbose_name=_("date start"))
    date_end = models.DateField(
        default=timezone.now,
        verbose_name=_("date end"))
    status = models.CharField(
        max_length=5,
        default=ActiveStatus.ACTIVE.value,
        choices=ActiveStatus.CHOICES.value,
        verbose_name=_("status"))
    document_link = models.URLField(
        null=True, blank=True,
        verbose_name=_('document link'),
        help_text=_('Provide support document link'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))

    def __str__(self):
        return "%s, %s" % (self.organization, self.position)


class AwardAbstract(BaseModel):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("name"))
    description = models.TextField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("description"))
    date = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('created date'))
    document_link = models.URLField(
        null=True, blank=True,
        verbose_name=_('document link'),
        help_text=_('Provide support document link'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))

    def __str__(self):
        return self.name


class SkillAbstract(BaseModel):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("name"))
    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("description"))
    level = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ],
        verbose_name=_('Skill level'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))

    @property
    def percent(self):
        return int(self.level) * 10

    def __str__(self):
        return self.name


class PublicationAbstract(BaseModel):
    class Meta:
        abstract = True

    title = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("title"))
    description = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("description"))
    publisher = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        null=True, blank=True,
        verbose_name=_("publisher"))
    date_published = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('published date'))
    document_link = models.URLField(
        null=True, blank=True,
        verbose_name=_('document link'),
        help_text=_('provide support document link'))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))

    def __str__(self):
        return self.title


class FamilyAbstract(BaseModel):
    class Meta:
        abstract = True

    relation = models.PositiveIntegerField(
        choices=FamilyRelation.CHOICES.value,
        default=FamilyRelation.OTHER.value,
        verbose_name=_("relation"))
    relationship = models.CharField(
        null=True, blank=True,
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("other relation"))
    name = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("name"))
    date_of_birth = models.DateField(
        null=True, blank=True,
        default=timezone.now,
        verbose_name=_('date of birth'))
    place_of_birth = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_('place of birth'))
    job = models.CharField(
        max_length=MaxLength.MEDIUM.value,
        verbose_name=_("job"))
    address = models.TextField(
        max_length=MaxLength.LONG.value,
        null=True, blank=True,
        verbose_name=_("address"))
    privacy = models.CharField(
        max_length=MaxLength.SHORT.value,
        choices=PrivacyStatus.CHOICES.value,
        default=PrivacyStatus.ANYONE.value,
        verbose_name=_("privacy"),
        help_text=_(
            'Designates who can see this information.'
        ))

    def __str__(self):
        return self.name
