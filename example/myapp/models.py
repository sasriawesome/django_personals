from django.db import models
from django.contrib import admin

from django_personals.models import Person
from django_personals.abstracts import (
    ContactAbstract,
    AddressAbstract,
    SocialAbstract,
    SkillAbstract,
    AwardAbstract,
    FormalEduAbstract,
    NonFormalEduAbstract,
    WorkingAbstract,
    VolunteerAbstract,
    PublicationAbstract,
    FamilyAbstract
)


# Create your models here.


class PersonContact(ContactAbstract):
    person = models.OneToOneField(
        Person, on_delete=models.CASCADE,
        related_name='contact')


class SocialMedia(SocialAbstract):
    person = models.OneToOneField(
        Person, on_delete=models.CASCADE,
        related_name='social_media'
    )


class PersonAddress(AddressAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='addresses'
    )


class Skill(SkillAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='skills'
    )


class Award(AwardAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='awards'
    )


class FormalEducation(FormalEduAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='formal_educations'
    )


class NonFormalEducation(NonFormalEduAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='non_formal_educations'
    )


class Working(WorkingAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='work_histories'
    )


class Volunteer(VolunteerAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='volunteers'
    )


class Publication(PublicationAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='publications'
    )


class Family(FamilyAbstract):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE,
        related_name='families'
    )
