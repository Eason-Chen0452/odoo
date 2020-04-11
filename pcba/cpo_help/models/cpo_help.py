# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class CpoHelp(models.Model):
    _name = 'cpo_help.help'

    TYPE_SELECT = [
        ('default', 'Default'),
        ('account', 'Account'),
        ('order', 'Order'),
    ]

    STATE_SELECT = [
        ('draft', 'Draft'),
        ('release', 'Release'),
        ('update', 'Update'),
        ('complete', 'Complete'),
        ('invalid', 'Invalid'),
    ]

    def _date_time_now(self):
        now = datetime.datetime.now()
        return now

    name = fields.Char(string="Name")
    type = fields.Selection(TYPE_SELECT, string="Help Type", dafault="default")
    update_time = fields.Datetime(string="Update Time", default=_date_time_now)
    content = fields.Html(string="Help Content")
    state = fields.Selection(STATE_SELECT, string="Status", default="draft")

    @api.multi
    def getHelpData(self, type):
        data = self.sudo().search([('type', '=', type), ('state', '=', 'release')])
        if data:
            return data
        return False

    @api.multi
    def help_search(self, data):
        if not data:
            pass
        obj = self.sudo().search([])
        for j in obj:
            if data in j.name.strip():
                return j
        return False
