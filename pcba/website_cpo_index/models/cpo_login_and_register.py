#-*- coding: utf-8 -*-
from odoo import models, fields, api
image = 'cpo_banner_img'

image_width = 300
image_high = 300
from odoo import tools
import datetime
image_size = (image_width, image_high)

class CpoBannerImage(models.Model):
    _name = 'cpo_login_and_register'
    _order = "sequence desc"

    SELECT_TYPE = [
        ('login_rigis', 'Login and Register')
    ]

    @api.multi
    def _get_create_time(self):
        nowtime = datetime.datetime.now()
        return nowtime

    sequence = fields.Integer(string="Sequence")
    cpo_description = fields.Text(string="Description")
    cpo_boolean = fields.Boolean(string="Log in / Register", default=False)
    cpo_type = fields.Selection(SELECT_TYPE, string="App types", default="login_rigis")
    cpo_date = fields.Date(string="Date", default=_get_create_time)
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
        if self.state in ['draft', 'maintain']:
            self.state = 'invalid'

        return True

    @api.multi
    def get_login_and_register_ingo(self):
        get_data = self.sudo().search([
            ('state', '=', 'release'),
            ('cpo_type', '=', 'login_rigis'),
            ('cpo_boolean', '=', True),
        ])
        return get_data
