#-*- coding: utf-8 -*-
from odoo import models, fields, api
image = 'cpo_banner_img'

image_width = 300
image_high = 300
from odoo import tools
import datetime

class CpoMcafeeAndGoogle(models.Model):
    _name = 'cpo_mcafee_and_google'
    _order = "sequence, id"

    sequence = fields.Integer(string="Sequence")
    cpo_data_title = fields.Char(string="Link Title")
    cpo_data_link = fields.Char(string="Script link")
