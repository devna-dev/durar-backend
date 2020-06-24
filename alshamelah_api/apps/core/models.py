from django.db import models


class BaseModel(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
