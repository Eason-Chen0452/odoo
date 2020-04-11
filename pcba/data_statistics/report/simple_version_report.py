# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class DataStatisticsReport(models.AbstractModel):
    _name = 'report.data_statistics.simple_version_qweb_report'

    def report_simple_version_search(self, data):
        """
        获取选择的数据类型进行查询
        :param data:
        :return:
        """
        values = None
        all_sql_data = {}
        now_time = datetime.datetime.now()

        if data.get('quote_data'):
            type = 'PCB and PCBA'
            today_pcb_pcba = self.simple_today_sql_data(now_time, type)
            week_pcb_pcba = self.simple_week_sql_data(now_time, type)
            month_pcb_pcba = self.simple_month_sql_data(now_time, type)
            all_sql_data.update({
                'pcb_and_pcba': {
                    'today_data': today_pcb_pcba,
                    'week_data': week_pcb_pcba,
                    'month_data': month_pcb_pcba
                }
            })
        if data.get('access_data'):
            type = 'Access'
            today_access = self.simple_today_sql_data(now_time, type)
            week_access = self.simple_week_sql_data(now_time, type)
            month_access = self.simple_month_sql_data(now_time, type)
            all_sql_data.update({
                'access': {
                    'today_data': today_access,
                    'week_data': week_access,
                    'month_data': month_access
                }
            })
        if data.get('source_data'):
            type = 'Source'
            today_source = self.simple_today_sql_data(now_time, type)
            week_source = self.simple_week_sql_data(now_time, type)
            month_source = self.simple_month_sql_data(now_time, type)
            all_sql_data.update({
                'source': {
                    'today_data': today_source,
                    'week_data': week_source,
                    'month_data': month_source
                }
            })

        values = {
            'all_sql_data': all_sql_data
        }
        return values

    @api.model
    def render_html(self, docids, data=None):
        docs = None
        report_obj = self.env['report']
        search_data = self.report_simple_version_search(data.get('vals'))
        # times = search_data.get('time')
        docs = self.env['website_cpo_index.all_partner_source'].search([])
        docargs = {
            'doc_ids': docids,
            'doc_model': 'report.data_statistics.get_data_statistics_qweb_report',
            'docs': docs,
            'data': search_data
        }
        return report_obj.render('data_statistics.simple_version_qweb_report', docargs)

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

    def simple_today_sql_data(self, now_time, type):
        data_dict = None
        today = 1
        time_ls = self.time_processing(now_time, today)
        if type == 'PCB and PCBA':
            data_dict = self.pcb_and_pcba_sql_data(time_ls, today)
        elif type == 'Access':
            data_dict = self.access_sql_data(time_ls, today)
        elif type == 'Source':
            data_dict = self.source_sql_data(time_ls, today)
        return data_dict

    def simple_week_sql_data(self, now_time, type):
        week_data = None
        week = 7
        time_ls = self.time_processing(now_time, week)
        if type == 'PCB and PCBA':
            week_data = self.pcb_and_pcba_sql_data(time_ls, week)
        elif type == 'Access':
            week_data = self.access_sql_data(time_ls, week)
        elif type == 'Source':
            week_data = self.source_sql_data(time_ls, week)
        return week_data

    def simple_month_sql_data(self, now_time, type):
        month_data = None
        month = 30
        time_ls = self.time_processing(now_time, month)
        if type == 'PCB and PCBA':
            month_data = self.pcb_and_pcba_sql_data(time_ls, month)
        elif type == 'Access':
            month_data = self.access_sql_data(time_ls, month)
        elif type == 'Source':
            month_data = self.source_sql_data(time_ls, month)
        return month_data

    def pcb_and_pcba_sql_data(self, time_ls, number):
        # PCB 和 PCBA SQL数据
        pcb_and_pcba_title = None
        if number == 1:
            pcb_and_pcba_title = _("PCB and PCBA quote data statistics (Today)")
        elif number == 7:
            pcb_and_pcba_title = _("PCB and PCBA quote data statistics (Week)")
        elif number == 30:
            pcb_and_pcba_title = _("PCB and PCBA quote data statistics (Month)")

        sql_data, tp_data, total_data, proportion = None, 0, 0, 0.0
        sql_data = self.pcb_and_pcba_sql_data_simple(time_ls)
        tp_data = self.env['cpo_pcb_and_pcba_record'].search_count([
            ('cpo_time', '>=', time_ls[0]),
            ('cpo_time', '<=', time_ls[1])])
        total_data = self.env['cpo_pcb_and_pcba_record'].search_count([])
        if total_data:
            proportion = float(format(float(tp_data) / float(total_data), '.3f')) * 100
        pcb_pcba = {
                'sql_data': sql_data,
                'tp_data': tp_data,
                'total_data': total_data,
                'proportion': proportion,
                'title': pcb_and_pcba_title,
                'time': time_ls
            }
        return pcb_pcba

    def access_sql_data(self, time_ls, number):
        # PCB 和 PCBA SQL数据
        access_title, access_data = None, None
        if number == 1:
            access_title = _("Website visits data statistics (Today)")
        elif number == 7:
            access_title = _("Website visits data statistics (Week)")
        elif number == 30:
            access_title = _("Website visits data statistics (Month)")
        sql_data, tp_data, total_data, proportion = None, 0, 0, 0.0
        sql_data = self.website_source_sql_data_simple(time_ls)
        tp_data = self.env['website_cpo_index.cpo_website_source'].search_count([
            ('cpo_time', '>=', time_ls[0]),
            ('cpo_time', '<=', time_ls[1])])
        total_data = self.env['website_cpo_index.cpo_website_source'].search_count([])
        if total_data:
            proportion = float(format(float(tp_data) / float(total_data), '.3f')) * 100
        access_data = {
                'sql_data': sql_data,
                'tp_data': tp_data,
                'total_data': total_data,
                'proportion': proportion,
                'title': access_title,
                'time': time_ls
            }
        return access_data

    def source_sql_data(self, time_ls, number):
        # PCB 和 PCBA SQL数据
        source_title, source_data = None, None
        if number == 1:
            source_title = _("Promotion channels data statistics (Today)")
        elif number == 7:
            source_title = _("Promotion channels data statistics (Week)")
        elif number == 30:
            source_title = _("Promotion channels data statistics (Month)")
        sql_data, tp_data, total_data, proportion = None, 0, 0, 0.0
        sql_data = self.partner_source_data_simple(time_ls)
        tp_data = self.env['website_cpo_index.all_partner_source'].search_count([
            ('cpo_time', '>=', time_ls[0]),
            ('cpo_time', '<=', time_ls[1])])
        total_data = self.env['website_cpo_index.all_partner_source'].search_count([])
        if total_data:
            proportion = float(format(float(tp_data) / float(total_data), '.3f')) * 100
        source_data = {
            'sql_data': sql_data,
            'tp_data': tp_data,
            'total_data': total_data,
            'proportion': proportion,
            'title': source_title,
            'time': time_ls
        }
        return source_data

    def pcb_and_pcba_sql_data_simple(self, time_ls):
        """
        PCB and PCBA 报价记录
        :param start_date:
        :param end_date:
        :return:
        """
        sql_data = None
        sql_str = """
                    SELECT 
                        MAX (ad.id) AS id, 
                        user_name AS user_name,
                        MAX (session_id) AS session_id,
                        SUM (
                            CASE
                                WHEN session_id IS NOT NULL THEN 1
                            ELSE 0 END
                        ) AS session_count,
                        MAX (cpo_country) AS cpo_country, 
                        MAX (user_ip) AS user_ip,
                        SUM (count_pcb) AS count_pcb,
                        SUM (count_pcba) AS count_pcba, 
                        SUM (count_num) AS count_num,
                        SUM (calculation) AS calculation,
                        SUM (comfirm) AS comfirm,
                        SUM (cart) AS cart,
                        SUM (selected) AS selected,
                        SUM (pending) AS pending
                    FROM 
                    (SELECT 
                        session_id AS session_id,
                        MAX (base_center.id) AS id,
                        MAX (base_center.name) AS user_name,
                        MAX (base_center.cpo_time) AS cpo_time,
                        MAX (base_center.cpo_country) AS cpo_country,
                        MAX (base_center.user_ip) AS user_ip,
                        SUM (
                            CASE
                                WHEN base_center.cpo_code='comfirm' THEN 1
                            ELSE 0 END
                        ) AS comfirm,
                        SUM (
                            CASE
                                WHEN base_center.cpo_code='calculation' THEN 1
                            ELSE 0 END
                        ) AS calculation,
                        SUM (
                            CASE
                                WHEN base_center.cpo_code='cart' THEN 1
                            ELSE 0 END
                        ) AS cart,
                        SUM (
                            CASE
                                WHEN base_center.cpo_code='selected' THEN 1
                            ELSE 0 END
                        ) AS selected,
                        SUM (
                            CASE
                                WHEN base_center.cpo_code='pending' THEN 1
                            ELSE 0 END
                        ) AS pending,
                        SUM (
                            CASE 
                                WHEN order_type='PCB' THEN 1
                                WHEN order_type='HDI' THEN 1
                                WHEN order_type='Rigid-FLex' THEN 1
                                WHEN order_type='PCB Package' THEN 1
                            ELSE 0 END)AS count_pcb,
                        SUM (
                            CASE 
                                WHEN order_type='PCBA' THEN 1 
                                WHEN order_type='PCBA Package Price' THEN 1 
                            ELSE 0 END) AS count_pcba,
                        COUNT (*) AS count_num
                    FROM cpo_pcb_and_pcba_record pcb_pcba LEFT OUTER JOIN 
                    (SELECT base.id,order_type,ps.name,user_ip,cpo_time,cpo_country,cpo_code,session_id FROM cpo_quotation_record_base base LEFT OUTER JOIN personal_center ps ON ps.id=base.user_name) AS base_center 
                        ON pcb_pcba.record_pcb_pcba_id=base_center.id
                        WHERE cpo_time >= '%s' AND cpo_time <= '%s'
                        GROUP by session_id
                        ORDER BY user_name) AS ad
                    GROUP BY user_name
                    ORDER BY user_name	
                    """ % (time_ls[0], time_ls[1])
        self.env.cr.execute(sql_str)
        sql_data = self.env.cr.dictfetchall()
        return sql_data

    def website_source_sql_data_simple(self, time_ls):
        """
        网站浏览记录
        :param start_date:
        :param end_date:
        :return:
        """
        sql_source = None
        sql_str = """
            SELECT 
                MAX(dd.id) AS id,
                MAX (wc.name) AS site_name,
                MAX(dd.user_name) AS user_name,
                COUNT(dd.user_name) AS session_num,
                MAX(dd.session_id) AS session_id,
                SUM(dd.session_num) AS source_num,
                MAX(dd.cpo_country) AS cpo_country,
                MAX(dd.cpo_ip) AS cpo_ip
            FROM 
                (SELECT 
                    MAX (s.id) AS id,
                    MAX (CASE
                    WHEN s.user_name IS NOT NULL THEN s.user_name
                    ELSE 'Public user' END) AS user_name,
                    COUNT (s.user_name) AS user_num,
                    ss.session_id AS session_id,
                    count(ss.session_id) AS session_num,
                    MAX (s.customer_related) AS customer_related,
                    MAX (s.cpo_country) AS cpo_country,
                    MAX (s.cpo_ip) AS cpo_ip 
                FROM website_cpo_index_cpo_website_source s LEFT OUTER JOIN cpo_session_association ss ON s.session_id=ss.id
                WHERE s.cpo_time >= '%s' AND s.cpo_time <= '%s'
                GROUP BY ss.session_id) dd
            LEFT OUTER JOIN
            website_cpo_index_cpo_partner_source wc
            ON dd.customer_related=wc.id
            group by user_name
            ORDER BY user_name ASC 
        """ % (time_ls[0], time_ls[1])
        self.env.cr.execute(sql_str)
        sql_source = self.env.cr.dictfetchall()
        return sql_source

    def partner_source_data_simple(self, time_ls):
        """
        网站推广记录（时间段内有多少从指定网站进来）
        :param start_date:
        :param end_date:
        :return:
        """
        partner_sd = None
        sql_str = """
            SELECT 
                max(psa.cpo_time) AS cpo_time,
                max(csa.name) AS session_id,
                sum(psa.site_count) as site_count,
                sum(psa.session_num) as session_num,
                psa.name as name
            FROM
            (SELECT
                max(ps.cpo_name) AS cpo_name,
                max(ps.cpo_time) AS cpo_time,
                ap.session_id,
                count(session_id) AS session_num,
                count(ps.name) as site_count,
                max(ps.name) AS name
            FROM website_cpo_index_all_partner_source as ap LEFT OUTER JOIN website_cpo_index_cpo_partner_source as ps
            ON ap.site_name=ps.id
            WHERE ap.cpo_time >= '%s' AND ap.cpo_time <= '%s'
            GROUP BY ap.session_id) AS psa
            LEFT OUTER JOIN cpo_session_association AS csa
            ON psa.session_id=csa.id
            GROUP BY psa.name
        """ % (time_ls[0], time_ls[1])
        self.env.cr.execute(sql_str)
        partner_sd = self.env.cr.dictfetchall()
        return partner_sd

