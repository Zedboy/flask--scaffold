#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


from avatar import app, config

if __name__ == '__main__':
    app.run(debug=config.DEBUG)