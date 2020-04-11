# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DataStatisticsReport(models.AbstractModel):
    _name = 'report.data_statistics.get_data_statistics_qweb_report'

    def report_get_search_data(self, data):
        """
        获取选择的数据类型进行查询
        :param data:
        :return:
        """
        data_dict = {}
        pcb_and_pcba_title = _("PCB and PCBA quote data statistics")
        source_title = _("Website visits data statistics")
        partner_title = _("Promotion channels data statistics")
        sql_data, tp_data, total_data, proportion = None, 0, 0, 0
        sql_source, tp_data_source, total_data_source, proportion_source = None, 0, 0, 0
        sql_partner, tp_data_partner, total_data_partner, proportion_partner = None, 0, 0, 0
        if data.get('vals'):
            start_date = data.get('vals').get('start_date') + ' 00:00:00'
            end_date = data.get('vals').get('end_date') + ' 23:59:59'
            quote_record = data.get('vals').get('quote_record')
            source_record = data.get('vals').get('source_data')
            access_data = data.get('vals').get('access_data')
            if quote_record:
                # PCB 和 PCBA SQL数据
                sql_data = self.pcb_and_pcba_sql_data(start_date, end_date)
                tp_data = self.env['cpo_pcb_and_pcba_record'].search_count([
                                            ('cpo_time', '>=', start_date),
                                            ('cpo_time', '<=', end_date)])
                total_data = self.env['cpo_pcb_and_pcba_record'].search_count([])
                if total_data:
                    proportion = float(format(float(tp_data) / float(total_data), '.3f')) * 100
                data_dict.update({
                    'pcb_pcba': {
                        'sql_data': sql_data,
                        'tp_data': tp_data,
                        'total_data': total_data,
                        'proportion': proportion,
                        'title': pcb_and_pcba_title
                    }
                })
            if access_data:
                sql_source = self.website_source_sql_data(start_date, end_date)
                tp_data_source = self.env['website_cpo_index.cpo_website_source'].search_count([
                    ('cpo_time', '>=', start_date),
                    ('cpo_time', '<=', end_date)])
                total_data_source = self.env['website_cpo_index.cpo_website_source'].search_count([])
                if total_data_source:
                    proportion_source = float(format(float(tp_data_source) / float(total_data_source), '.3f')) * 100
                data_dict.update({
                    'sql_source': {
                        'sql_data': sql_source,
                        'tp_data': tp_data_source,
                        'total_data': total_data_source,
                        'proportion': proportion_source,
                        'title': source_title
                    }
                })
            if source_record:
                sql_partner = self.partner_source_data(start_date, end_date)
                tp_data_partner = self.env['website_cpo_index.all_partner_source'].search_count([
                    ('cpo_time', '>=', start_date),
                    ('cpo_time', '<=', end_date)])
                total_data_partner = self.env['website_cpo_index.all_partner_source'].search_count([])
                if total_data_partner:
                    proportion_partner = float(format(float(tp_data_partner) / float(total_data_partner), '.2f')) * 100
                data_dict.update({
                    'sql_partner': {
                        'sql_data': sql_partner,
                        'tp_data': tp_data_partner,
                        'total_data': total_data_partner,
                        'proportion': proportion_partner,
                        'title': partner_title
                    }
                })

            values = {
                'data_dict': data_dict,
                "time": [data.get('vals').get('start_date'), data.get('vals').get('end_date')],

            }
        return values

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        search_data = self.report_get_search_data(data)
        times = search_data.get('time')
        docs = self.env['website_cpo_index.all_partner_source'].search([('cpo_time', '>=', times[0]), ('cpo_time', '<=', times[1])])
        docargs = {
            'doc_ids': docids,
            'doc_model': 'report.data_statistics.get_data_statistics_qweb_report',
            'docs': docs,
            'values': search_data
        }
        return report_obj.render('data_statistics.get_data_statistics_qweb_report', docargs)

    def pcb_and_pcba_sql_data(self, start_date, end_date):
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
                    """ % (start_date, end_date)
        self.env.cr.execute(sql_str)
        sql_data = self.env.cr.dictfetchall()
        return sql_data

    def website_source_sql_data(self, start_date, end_date):
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
        """ % (start_date, end_date)
        self.env.cr.execute(sql_str)
        sql_source = self.env.cr.dictfetchall()
        return sql_source

    def partner_source_data(self, start_date, end_date):
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
        """ % (start_date, end_date)
        self.env.cr.execute(sql_str)
        partner_sd = self.env.cr.dictfetchall()
        return partner_sd

