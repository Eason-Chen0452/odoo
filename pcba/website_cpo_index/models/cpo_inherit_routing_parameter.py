# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _


class CPOExceptionKeyword(models.Model):
    _inherit = 'routing_parameter.exception_keyword'

    site_name = fields.Many2one('website_cpo_index.cpo_partner_source', string="Site name")


class CPOExternalKeyword(models.Model):
    _inherit = 'routing_parameter.external_keyword'

    site_name = fields.Many2one('website_cpo_index.cpo_partner_source', string="Site name")


class CPOInternalKeyword(models.Model):
    _inherit = 'routing_parameter.internal_keyword'

    site_name = fields.Many2one('website_cpo_index.cpo_partner_source', string="Site name")


class CPOLinkRule(models.Model):
    _inherit = 'routing_parameter.link_rule'

    partner_source_id = fields.One2many('website_cpo_index.all_partner_source', 'type', string="Pantner ID")
