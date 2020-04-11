# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time, datetime


class CPOLinkRule(models.Model):
    _name = 'routing_parameter.link_rule'

    SELECTION_TYPE = [
        ('search_engine', 'Search engine'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('mail', 'Mail'),
        ('other', 'Other')
    ]

    @api.model
    def _cpo_now_time(self):
        now_time = fields.Datetime.now()
        return now_time

    name = fields.Char(string="Name", required=True)
    type = fields.Selection(SELECTION_TYPE, string="Source type", required=True)
    url = fields.Char(string="URL", required=True)
    cpo_time = fields.Datetime(string="Last update time", default=_cpo_now_time)
    utm_source_id = fields.Many2one('utm.source', string="UTM source")

    @api.model
    def cpoAssociatedSource(self):
        """
        定时处理关联ＵＴＭ数据（暂定）
        :return:
        """
        cpo_source = self.env['website_cpo_index.all_partner_source'].sudo().search([])
        link_rule = self.sudo().search([])
        utm_source = self.env['utm.source'].sudo().search([])
        for lr in link_rule:
            link = lr.url
            if cpo_source:
                for cs in cpo_source:
                    if link in cs.cpo_name or cs.cpo_name in link:
                        cs.update({
                            'type': lr.id
                        })
            if utm_source:
                for us in utm_source:
                    if us.type == lr.type:
                        lr.utm_source_id = us.id
