#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField


class AvatarForm(Form):
    avatar_url = FileField(u'头像图片', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], u'只能上传jpg, jpeg, png格式的图片')
    ])
    x1 = StringField(u'x1')
    y1 = StringField(u'y1')
    x2 = StringField(u'x2')
    y2 = StringField(u'y2')
    w = StringField(u'w')
    h = StringField(u'h')

