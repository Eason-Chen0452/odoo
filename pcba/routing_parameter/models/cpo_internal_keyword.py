# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CPOInternalKeyword(models.Model):
    _name = 'routing_parameter.internal_keyword'

    key = fields.Char(string="Key")
    value = fields.Char(string="Value")
    domain_name = fields.Char(string="Domain name")
    cpo_time = fields.Datetime(string="Last update time")
    # site_name = fields.Many2one('website_cpo_index.cpo_partner_source', string="Site name")
