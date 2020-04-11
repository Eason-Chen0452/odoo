# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class DataStatistics(models.TransientModel):
    _name = 'data_statistics.data_statistics'

    def _start_time(self):
        nowtime = datetime.datetime.now()
        return nowtime

    start_date = fields.Date(string="Start Time", required=True, default=_start_time)
    end_date = fields.Date(string="End Time", required=True, default=_start_time)
    quote_record = fields.Boolean(string="PCB and PCBA quotation record", default=True)
    source_data = fields.Boolean(string="Promotion statistics", default=True)
    access_data = fields.Boolean(string="Access to records", default=True)

    def time_processing(self, now_time, time_delta):
        """
        时间差处理，当天，本周，本月
        :param now_time:
        :param time_delta:
        :return:
        """
        time_diff, start_time, end_time = None, None, None
        if time_delta == 1:
            time_diff = now_time - datetime.timedelta(hours=now_time.hour, minutes=now_time.minute,
                                                   seconds=now_time.second, microseconds=now_time.microsecond)
            start_time = datetime.datetime.strftime(time_diff, '%Y-%m-%d %H:%M:%S')
        else:
            time_diff = now_time - datetime.timedelta(time_delta)
            start_time = datetime.datetime.strftime(time_diff, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
        times = [start_time, end_time]
        return times

    @api.multi
    def get_to_today(self):
        now_time = datetime.datetime.now()
        time_ls = self.time_processing(now_time, 1)
        self.start_date = time_ls[0]
        self.end_date = time_ls[1]
        vals = self.get_data_statistics()
        return self.env['report'].get_action(0, 'data_statistics.get_data_statistics_qweb_report', data=vals.get('data'))

    @api.multi
    def get_to_week(self):
        now_time = datetime.datetime.now()
        time_ls = self.time_processing(now_time, 7)
        self.start_date = time_ls[0]
        self.end_date = time_ls[1]
        vals = self.get_data_statistics()
        return self.env['report'].get_action(0, 'data_statistics.get_data_statistics_qweb_report', data=vals.get('data'))

    @api.multi
    def get_to_month(self):
        now_time = datetime.datetime.now()
        time_ls = self.time_processing(now_time, 30)
        self.start_date = time_ls[0]
        self.end_date = time_ls[1]
        vals = self.get_data_statistics()
        return self.env['report'].get_action(0, 'data_statistics.get_data_statistics_qweb_report', data=vals.get('data'))

    @api.multi
    def get_data_statistics(self):
        data = None
        self.ensure_one()
        [data] = self.read()
        user_ids = self.env['res.users'].search([]).ids
        data['name'] = user_ids
        vals = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'quote_record': self.quote_record,
            'source_data': self.source_data,
            'access_data': self.access_data
        }
        value = {
            'ids': [],
            'model': 'website_cpo_index.cpo_partner_source',
            'form': data,
            'vals': vals,
        }
        return self.env['report'].get_action(0, 'data_statistics.get_data_statistics_qweb_report', data=value)
