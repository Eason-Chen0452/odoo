#-*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime

class CpoGoogleAnalytics(models.Model):
    _name = 'cpo_google_analytics'
    _order = "id desc"

    cpo_browse_link = fields.Char(string="Browse Links", readonly=True)
    cpo_browse_time = fields.Char(string="Browse Time", readonly=True)
    cpo_recor_time = fields.Char(string="Recording Time", readonly=True)
    cpo_customer = fields.Char(string="Client", readonly=True)
    cpo_ip = fields.Char(string="IP Address", readonly=True)


    @api.model
    def add_google_analytics(self, cpo_browse_link, cpo_browse_time, cpo_ip):
        vals = {
            'cpo_browse_link': cpo_browse_link,
            'cpo_browse_time': cpo_browse_time,
            'cpo_recor_time': datetime.datetime.now(),
            'cpo_customer': self.env.user.name,
            'cpo_ip': cpo_ip,
        }

        self.create(vals)

        return True





