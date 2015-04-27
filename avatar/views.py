#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import logging
import os
from PIL import Image
from flask import render_template, request, flash
from avatar import app
from avatar.forms import AvatarForm
from .utils import mkdir, mkdirbysize, mkdirbydate, safefilename, thumbnail


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/avatar', methods=['GET', 'POST'])
def avatar():
    form = AvatarForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            safe_filename = safefilename(form.avatar_url.data.filename)
            avatar_path = mkdir(app.config['AVATAR'])
            size150_path = mkdirbysize(avatar_path, size=150)
            date150_path, date_dir = mkdirbydate(size150_path)
            avatar_url_sql = os.path.join(date_dir, safe_filename)
            im = rim = crop150 = None
            try:
                im = Image.open(form.avatar_url.data)
                width, height = im.size
                nwidth, nheight = thumbnail(width, height, 500.0)
                rim = im.resize((nwidth, nheight), Image.ANTIALIAS)
                logging.info('picture {}, {} has been resize to {} {}'.format(width, height, nwidth, nheight))
                size = (
                int(form.data.get('x1')), int(form.data.get('y1')), int(form.data.get('x2')), int(form.data.get('y2')))
                crop150 = rim.crop(size).resize((150, 150), Image.ANTIALIAS)
                logging.info('picture has been crop')
                crop150.save(os.path.join(date150_path, safe_filename))
                logging.info('picture has upload successful')
                flash(u'上传头像成功', category='success')
            except:
                logging.error('picture crop and save error')
                flash(u'上传头像失败', category='error')
            finally:
                if crop150:
                    crop150.close()
                if rim:
                    rim.close()
                if im:
                    im.close()

    template_name_or_list = 'avatar.html'
    return render_template(**locals())
