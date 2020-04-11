# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class ContactusMessage(models.Model):
    _name = 'contactus_message.contactus'
    _order = 'id desc, date desc'

    def _get_data_time(self):
        nowtime = datetime.datetime.now()
        return nowtime

    STATE_SELECTION = [
        ('read', 'Read'),
        ('unread', 'Unread'),
    ]

    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    company = fields.Char(string="Company")
    support_type = fields.Char(string="Service support type")
    content = fields.Text(string="Content")
    date = fields.Datetime(string="Message time", dafault=_get_data_time)
    read_time = fields.Datetime(string="Read time")
    change = fields.Char(string="Status", compute="_change_status", store=False)
    state = fields.Selection(STATE_SELECTION, string="Status", default="unread")

    @api.multi
    def cu_create(self, vals):
        cu_data = self.create(vals)
        return cu_data

    def _change_status(self):
        time = fields.Datetime.now()
        self._cr.execute("""UPDATE contactus_message_contactus SET state='read',read_time='%s' WHERE id=%d""" % (time, self.id))
        return True


