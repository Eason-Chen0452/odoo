#-*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class CpoCookieDuration(models.Model):
    """
     设置cookie时长
     """

    _name = "cpo_cookie_duration"


    @api.multi
    def _get_user_name(self):
        user_name = self.env.user.name
        return user_name

    @api.multi
    def _get_user_id(self):
        user_id = self.env.user.id
        return user_id

    @api.multi
    def _get_create_time(self):
        nowTime = datetime.datetime.now()
        return nowTime

    user_id = fields.Char(string="User ID", default=_get_user_id)
    user_name = fields.Char(string="User Name", default=_get_user_name)
    cookie_time = fields.Float(string="Cookie Duration")
    cpo_time = fields.Datetime(string="Create Time", default=_get_create_time)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('release', 'Release'),
        ('maintain', 'Maintenance update'),
        ('complete_maintain', 'Complete maintenance update'),
        ('invalid', 'Become invalid')
    ], string='Status', copy=False, index=True, default='draft')

    @api.multi
    def do_draft(self):
        if self.state == 'invalid':
            self.state = 'draft'
        return True


    @api.multi
    def do_release(self):
        if self.state == 'draft':
            self.state = 'release'
        return True


    @api.multi
    def do_maintain(self):
        if self.state == 'release':
            self.state = 'maintain'
        return True

    @api.multi
    def do_complete_maintain(self):
        if self.state == 'maintain':
            self.state = 'release'
        return True


    @api.multi
    def do_invalid(self):

        self.state = 'invalid'
        return True


