#-*- coding: utf-8 -*-
from odoo import models, fields, api
image = 'cpo_banner_img'

image_width = 300
image_high = 300
from odoo import tools
import datetime
image_size = (image_width, image_high)

class CpoBannerImage(models.Model):
    _name = 'cpo_banner_image'
    _order = "sequence desc"

    SELECT_TYPE = [
        ('svg', 'SVG'),
        ('png', 'PNG'),
        ('jpg', 'JPG'),
    ]
    sequence = fields.Integer(string="Sequence")
    cpo_banner_title = fields.Char(string="Title")
    cpo_banner_date = fields.Date(string="Date")
    cpo_image_type = fields.Selection(SELECT_TYPE, string="Image Type", default="png")
    cpo_banner_img = fields.Binary(string="Image", attachment=True)
    cpo_main_color = fields.Char(string="Main color tone")
    cpo_banner_description = fields.Text(string="Description")
