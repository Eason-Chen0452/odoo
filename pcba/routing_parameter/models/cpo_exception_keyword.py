# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CPOExceptionKeyword(models.Model):
    _name = 'routing_parameter.exception_keyword'

    key = fields.Char(string="Key")
    value = fields.Char(string="Value")
    domain_name = fields.Char(string="Domain name")
    cpo_time = fields.Datetime(string="Last update time")

