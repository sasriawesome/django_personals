from django.contrib import admin
from .models import (
    Person,
    PersonContact,
    PersonAddress,
    SocialMedia,
    Skill,
)


class PersonContactInline(admin.StackedInline):
    model = PersonContact
    extra = 0


class PersonAddressInline(admin.StackedInline):
    model = PersonAddress
    extra = 0


class SocialMediaInline(admin.StackedInline):
    model = SocialMedia
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    inlines = [
        PersonContactInline,
        PersonAddressInline,
        SocialMediaInline,
        SkillInline
    ]


admin.site.register(Person, PersonAdmin)
