#-*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class CpoWebsiteSourceSet(models.Model):
    """
    记录网站来源，例如来自百度的推广等。
    设置定时删除来源记录，默认30天
    """

    _name = "cpo_website_source_setting"
    _order = "sequence desc"

    SELECTION = [
        ('draft', 'Draft'),
        ('active', 'Activating'),
        ('logout', 'Logout')
    ]
    CODE_SELECTION = [
        ('source', 'Website Source')
    ]

    @api.model
    def _default_user_name(self):
        user_name = self.env.user.name
        return user_name

    @api.model
    def _default_time(self):
        create_time = datetime.datetime.now()
        return create_time

    sequence = fields.Integer(string='Sequence')
    cpo_description = fields.Text(string="Description")
    set_time = fields.Integer(string="Record cycle setting", default=30)
    cpo_operator = fields.Char(string="Operator", readonly=True, default=_default_user_name)
    cpo_time = fields.Datetime(string="Last update time", readonly=True, default=_default_time)
    state = fields.Selection(SELECTION, string="Status", default='draft')
    cpo_code = fields.Selection(CODE_SELECTION, string="Genre", default='source')

    @api.multi
    def cpoRegularlyCleanRecord(self):
        time_delta = 0
        get_time = self.sudo().search([
            ('cpo_code', '=', 'source'),
            ('state', '=', 'active'),
        ])
        if get_time:
            for t in get_time:
                time_delta = int(t.set_time)
                break
        cpo_set_time = self.cpo_set_time(time_delta)
        get_data = self.env['website_cpo_index.cpo_website_source'].sudo().search([
            ('cpo_time', '<', cpo_set_time)
        ])
        get_data.unlink()
        return True

    @api.multi
    def do_active(self):
        if self.state == 'draft':
            self.state = "active"
        return True

    @api.multi
    def do_logout(self):
        if self.state == 'active':
            self.state = "logout"
        return True

    def cpo_set_time(self, time):
        format_pattern = "%Y-%m-%d %H:%M:%S"
        datetime_now_utc = fields.Datetime.to_string(
            fields.Datetime.context_timestamp(self.env.user.with_context({'tz': 'utc'}), fields.Datetime.from_string(fields.Datetime.now())))
        get_time = datetime.datetime.strptime(datetime_now_utc, format_pattern) - datetime.timedelta(days=time)
        comparison_time = get_time.strftime(format_pattern)
        return comparison_time
