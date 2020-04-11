# -*- coding: utf-8 -*-

from odoo import fields, models, api
image = 'ad_photo'

image_width = 300
image_high = 300

from odoo import tools
import datetime
image_size = (image_width, image_high)

class CpoNotification(models.Model):
    _name = 'cpo_notification'

    def _get_notice_now_time(self):
        nowTime = datetime.datetime.now()
        return nowTime

    notice_title = fields.Char(string="Notification Title")
    notice_content = fields.Text(string="Notification content")
    notice_description = fields.Text(string="Description")
    notice_start_time = fields.Date(string="Start time")
    notice_end_time = fields.Date(string="End time")
    notice_bg = fields.Char(string="Notification Background")
    notice_link = fields.Char(string="Notification Link", default="/natification")
    notice_now_time = fields.Date(string="Notification Time", default=_get_notice_now_time)
    notice_bool = fields.Boolean(string="Effective")
    # notice_execution = fields.Date(string="Execution Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('release', 'Release'),
        ('update', 'Update'),
        ('complete', 'Complete update'),
        ('invalid', 'Become invalid')
    ], string='Status', copy=False, index=True, default='draft')

    @api.multi
    def do_release(self):
        if self.state == 'draft':
            self.state = 'release'
        return True

    @api.multi
    def do_update(self):
        if self.state == 'release':
            self.state = 'update'
        return True

    @api.multi
    def do_complete(self):
        if self.state == 'update':
            self.state = 'release'

        return True

    @api.multi
    def do_invalid(self):
        if self.state in ['draft', 'update', 'release']:
            self.state = 'invalid'
        return True
