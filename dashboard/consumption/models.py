# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tkinter import CASCADE

from django.db import models

# Create your models here.


class User(models.Model):
    """ユーザー情報

    Args:
        models (_type_): _description_
    """
    id = models.CharField(max_length=6, primary_key=True)
    area = models.CharField(max_length=6)
    tariff = models.CharField(max_length=6)


class Data(models.Model):
    """電力消費量

    Args:
        models (_type_): _description_
    """
    # ユーザー単位で集計するケースを想定してユーザーIDをもたせる
    datetime = models.DateTimeField(null=True, blank=False)
    consumption = models.FloatField(default=0)
    # ユーザー情報と関連付ける
    user = models.ForeignKey(User, on_delete=CASCADE)
