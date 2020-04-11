#-*- coding: utf-8 -*-
from odoo import models, fields, api

class cpoWebsiteSelectURL(models.Model):
    _name = 'cpo_select_url'
    _order = "sequence asc"

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string="Website Name")
    active = fields.Boolean('Active', default=False)
    select_url = fields.Many2many('cpo_add_url', string="Website Name")



class cpoWebsiteAddURL(models.Model):
    _name = 'cpo_add_url'
    _order = "sequence asc"

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string="URL")