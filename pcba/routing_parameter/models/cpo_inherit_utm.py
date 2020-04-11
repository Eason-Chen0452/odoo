# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _


class UtmSource(models.Model):
    _inherit = 'utm.source'
    _description = 'Source'

    SELECTION_TYPE = [
        ('search_engine', 'Search engine'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('mail', 'Mail'),
        ('other', 'Other')
    ]

    type = fields.Selection(SELECTION_TYPE, string="Source Type", required=True)
    partner_source_id = fields.One2many('routing_parameter.link_rule', 'utm_source_id', string="Source type")

