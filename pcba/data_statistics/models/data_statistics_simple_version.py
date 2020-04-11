# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class DataStatistics(models.TransientModel):
    _name = 'data_statistics.simple_version'

    pcb_quote = fields.Boolean(string="PCB quotation record", default=True)
    pcba_quote = fields.Boolean(string="PCBA quotation record", default=True)
    quote_data = fields.Boolean(string="PCB and PCBA quotation record", default=True)
    source_data = fields.Boolean(string="Promotion statistics", default=True)
    access_data = fields.Boolean(string="Access to records", default=True)

    #
    @api.multi
    def get_simple_data_statistics(self):
        vals = None
        vals = {
            'pcb_quote': self.pcb_quote,
            'pcba_quote': self.pcba_quote,
            'quote_data': self.quote_data,
            'source_data': self.source_data,
            'access_data': self.access_data
        }
        value = {
            'ids': [],
            'model': 'website_cpo_index.cpo_partner_source',
            'vals': vals,
        }
        return self.env['report'].get_action(0, 'data_statistics.simple_version_qweb_report', data=value)
