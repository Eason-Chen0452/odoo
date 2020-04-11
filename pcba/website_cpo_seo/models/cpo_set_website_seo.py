#-*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
url_name = [
    ('homepage', 'Index Page'),
    ('pcb', 'PCB Page'),
    ('pcba', 'PCBA Page'),
    ('stencil', 'Stencil Page'),
    ('contactus', 'Contactus Page'),
    ('cart', 'Cart Page'),
    ('my', 'Account Page'),
]
class cpoWebsite(models.Model):
    _name = 'cpo_set_website_seo'


    cpo_page_name = fields.Selection(url_name, string="URL Name")
    cpo_title = fields.Char(string="Page Title")
    cpo_keyworks = fields.Text(string="Key Works")
    cpo_description = fields.Text(string="Description")
    cpo_date = fields.Datetime(compute='_compute_date', string="Date")

    @api.multi
    @api.depends('cpo_date')
    def _compute_date(self):
        self.cpo_date = datetime.datetime.now()