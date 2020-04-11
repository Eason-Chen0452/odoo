# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class QuotaRecordSetting(models.Model):
    _name = 'cpo_function_setting.quota_record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    SELECTION = [
        ('draft', 'Draft'),
        ('active', 'Activating'),
        ('change', 'Change'),
        ('obsolete', 'Obsolete')
    ]

    name = fields.Char(string="Setting name")
    description = fields.Text(string="Setting description")
    enable = fields.Boolean(string="Setting Enable", default=False)
    interval = fields.Integer(string="Setting interval", default="4")
    state = fields.Selection(SELECTION, default="draft", string="Status", track_visibility='always')

    @api.model
    def get_quota_record_set(self):
        flag = False
        cpo_model = self.env['ir.model'].sudo().search([('model', '=', 'cpo_function_setting.quota_record')])
        if cpo_model:
            data = self.sudo().search([('interval', '>', 0), ('state', '=', 'active'), ('enable', '=', True)], limit=1)
            return data
        else:
            return flag


    @api.multi
    def do_active(self):
        """
        激活
        :return:
        """
        if self.state == 'draft':
            self.state = "active"
        return True

    @api.multi
    def do_obsolete(self):
        """
        作废
        :return:
        """
        if self.state == 'active':
            self.state = "obsolete"
        return True

    @api.multi
    def do_change(self):
        """
        变更
        :return:
        """
        if self.state == 'active':
            self.state = "change"
        return True

    @api.multi
    def do_complete(self):
        """
        完成
        :return:
        """
        if self.state == 'change':
            self.state = "active"
        return True

    @api.multi
    def do_recovery(self):
        """
        恢复
        :return:
        """
        if self.state == 'obsolete':
            self.state = "active"
        return True

