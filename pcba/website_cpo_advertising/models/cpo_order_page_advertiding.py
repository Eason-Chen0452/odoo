# -*- coding: utf-8 -*-

from odoo import fields, models, api
image = 'ad_photo'

image_width = 300
image_high = 300

from odoo import tools
import datetime

image_size = (image_width, image_high)

class websitePageAdvertising(models.Model):
    _name = 'cpo_page_advertising'

    ad_page_title = fields.Char(string="Title")
    ad_image = fields.Binary(string="AD Image")