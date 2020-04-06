import uuid
from django.db import models

UUID = {
    'default': uuid.uuid4,
    'unique': True,
    'primary_key': True,
    'editable': True
}