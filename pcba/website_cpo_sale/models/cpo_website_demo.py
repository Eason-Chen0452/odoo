# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _

class CpoWebsiteDemo(models.Model):
    _name = 'cpo.website.demo'

    name = fields.Char('Name')
    class_code = fields.Char('Class Code')
    body_html = fields.Html('Body', sanitize=False)
