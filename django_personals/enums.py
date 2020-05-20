import enum
from django.utils.translation import ugettext_lazy as _


class MaxLength(enum.Enum):
    SHORT = 128
    MEDIUM = 256
    LONG = 512
    XLONG = 1024
    TEXT = 2048
    RICHTEXT = 10000


class ActiveStatus(enum.Enum):
    ACTIVE = 'ACT'
    INACTIVE = 'INC'

    CHOICES = (
        (ACTIVE, _("active").title()),
        (INACTIVE, _("inactive").title()),
    )


class PrivacyStatus(enum.Enum):
    ANYONE = 'anyone'
    USERS = 'users'
    FRIENDS = 'friends'
    STUDENTS = 'students'
    TEACHERS = 'teachers'
    EMPLOYEES = 'employees'
    MANAGERS = 'managers'
    ME = 'me'

    CHOICES = (
        (ANYONE, _("anyone").title()),
        (USERS, _('all users').title()),
        (FRIENDS, _('all friends').title()),
        (STUDENTS, _('all students').title()),
        (TEACHERS, _('all teachers').title()),
        (EMPLOYEES, _('all employees').title()),
        (MANAGERS, _('all managers').title()),
        (ME, _('only me').title())
    )


class Gender(enum.Enum):
    MALE = 'L'
    FEMALE = 'P'

    CHOICES = (
        (MALE, _("male").title()),
        (FEMALE, _("female").title()),
    )


class AddressName(enum.Enum):
    HOME = 'home'
    OFFICE = 'office'

    CHOICES = (
        (HOME, _("home").title()),
        (OFFICE, _("office").title()),
    )


class EducationStatus(enum.Enum):
    FINISHED = 'FNS'
    ONGOING = 'ONG'
    UNFINISHED = 'UNF'

    CHOICES = (
        (FINISHED, _("finished").title()),
        (ONGOING, _("ongoing").title()),
        (UNFINISHED, _("unfinished").title()),
    )


class WorkingStatus(enum.Enum):
    CONTRACT = 'CTR'
    FIXED = 'FXD'
    OUTSOURCE = 'OSR'
    ELSE = 'ELS'

    CHOICES = (
        (CONTRACT, _("contract").title()),
        (FIXED, _("fixed").title()),
        (OUTSOURCE, _("outsource").title()),
        (ELSE, _("else").title())
    )


class FamilyRelation(enum.Enum):
    FATHER = 1
    MOTHER = 2
    SIBLING = 3
    CHILD = 4
    HUSBAND = 5
    WIFE = 6
    OTHER = 99

    CHOICES = (
        (FATHER, _('father').title()),
        (MOTHER, _('mother').title()),
        (HUSBAND, _('husband').title()),
        (WIFE, _('wife').title()),
        (CHILD, _('children').title()),
        (SIBLING, _('sibling').title()),
        (OTHER, _('other').title()),
    )
