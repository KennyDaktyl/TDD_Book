from django.db import models


class Item(models.Model):
    text = models.TextField()
    list_fk = models.ForeignKey('List',
                                default=None,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=None)


class List(models.Model):
    text = models.TextField()
