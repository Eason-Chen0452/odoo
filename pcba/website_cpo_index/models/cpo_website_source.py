#-*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

SELECT_INTENTION = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

class CpoWebsiteSource(models.Model):
    """
    记录网站来源，例如来自百度的推广等。
    """

    _name = "cpo_website_source"
    _order = "sequence desc"

    sequence = fields.Integer(string='Sequence')
    user_id = fields.Char(string="User ID")
    user_name = fields.Char(string="User Name")
    cpo_source = fields.Char(string="Website Source")
    cpo_ip = fields.Char(string="User IP")
    cpo_country = fields.Char(string="Country")
    cpo_time = fields.Datetime(string="Create Time")

    @api.multi
    def get_data_create(self, vals):
        self.sudo().create(vals)
        return True

    @api.multi
    def get_data_search(self, vals):
        data = self.sudo().search(vals)
        return data
