# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class MarketingStrategyAnalysis(models.Model):
#     _name = 'crm.msa_alone'
#     _description = 'Marketing Strategy Analysis'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'id desc'
#
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
