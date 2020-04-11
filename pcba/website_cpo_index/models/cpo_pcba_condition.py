# -*- coding: utf-8 -*-

from odoo import fields, models, api
image = 'ad_photo'

image_width = 300
image_high = 300

from odoo import tools
import datetime
image_size = (image_width, image_high)

class CpoPCBACondition(models.Model):
    _name = 'cpo_pcba_condition'
    _order = "id desc,sequence desc"

    CONDITION_SELECT = [
        ('no', 'Components Provided by Customer'),
        ('yes', 'Components Free'),
        ('standard', 'Normal SMT Process')
    ]

    sequence = fields.Integer(string="Squence")
    condition_photo = fields.Binary(string="Picture")
    condition_type = fields.Selection(CONDITION_SELECT, string="Condition Type", default="no")
    condition_title = fields.Char(string="Condition Title")
    condition_one = fields.Char(string="Condition One")
    condition_two = fields.Char(string="Condition Two")
    condition_three = fields.Char(string="Condition Three")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('release', 'Release'),
        ('maintain', 'Maintenance update'),
        ('complete_maintain', 'Complete maintenance update'),
        ('invalid', 'Become invalid')
        ], string='Status', copy=False, index=True, default='draft')
    condition_now_time = fields.Datetime(string="Notification Create Time", compute='_get_create_time')
    condition_link = fields.Char(string="Quotation Link")

    @api.multi
    def _get_create_time(self):
        nowTime = datetime.datetime.now()
        self.ad_now_time = nowTime
        return True

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
        if self.state in ['draft', 'maintain']:
            self.state = 'invalid'

        return True
