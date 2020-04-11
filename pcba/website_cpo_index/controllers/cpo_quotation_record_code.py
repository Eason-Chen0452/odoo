# -*- coding: utf-8 -*-
from odoo import http, tools, _, fields
from odoo.http import request
import werkzeug
import base64
import datetime
import time
from decimal import Decimal
import Queue
import logging

_logger = logging.getLogger(__name__)

class CpoQuotationRecordCode(object):
    """
    报价记录，网页浏览记录
    """

    def cpo_record_time_setting(self):
        """
        设置报价记录的更新时间，单位为小时
        :return:
        """
        time_delta = None
        record_time = request.env['cpo_function_setting.quota_record'].sudo().get_quota_record_set()
        if record_time:
            time_delta = record_time.interval
        else:
            time_delta = 4
        return time_delta

    def cpo_get_record_data(self, values, cpo_code):
        try:
            cpo_s_u = self.cpo_get_user_info()
            partner_info = request.env['cpo_session_association'].sudo().check_session_info(cpo_s_u)
            partner_user = {'partner_info': partner_info.get('get_data')}
            user_info = {
                # 'user_id': request.env.user.id,
                'user_name': partner_info.get('get_customer'),
            }
            session_data = self.cpo_get_user_data()
            comfirm_data = self.cpo_get_all_data(values)
            record_data = dict(comfirm_data.items() + session_data.items() + user_info.items() + partner_user.items())
            self.comparison_time(record_data, cpo_code)
        except Exception, e:
            pass


    def cpo_get_all_data(self, values):
        product_name = values.get('product').name
        if product_name == 'PCB':
            cpo_data = self.cpo_get_pcb_record(values)
        if product_name == 'PCBA':
            cpo_data = self.cpo_get_pcba_record(values)
        return cpo_data

    def cpo_get_pcb_record(self, values):
        if values.get('number_of_step'):
            order_type = 'HDI'
        elif values.get('cpo_flex_number'):
            order_type = 'Rigid-FLex'
        elif values.get('package'):
            order_type = 'PCB Package'
        else:
            order_type = 'PCB'

        record_data = {
            'order_type': order_type,
            'quantity': int(values.get('cpo_quantity') or 0),
            'width': float(values.get('pcb_width') or 0),
            'lenght': float(values.get('pcb_length') or 0),
            'thickne': float(values.get('pcb_thickness') or 0),
            'file_name': '',
            'cpo_time': datetime.datetime.now(),
            'total': values.get('all_prices').get('all_fee'),
            'panel_size': values.get('pcb_pcs_size'),
            'item_qty': values.get('pcb_item_size'),
            'material': values.get('pcb_type'),
            'inner_copper': float(values.get('pcb_inner_copper') or 0),
            'outer_copper': float(values.get('pcb_outer_copper') or 0),
            'layers': values.get('pcb_layer'),
            'mask_color': values.get('pcb_solder_mask'),
            'silkscreen_color': values.get('pcb_silkscreen_color'),
            'surface': values.get('pcb_surface'),
            'e_test': values.get('pcb_test')
        }
        return record_data

    def cpo_get_pcba_record(self, values):
        if values.get('pcba_package_surface'):
            order_type = 'PCBA Package Price'
            record_data = {
                'order_type': order_type,
                'quantity': int(values.get('pcba_package_qty') or 0),
                'width': float(values.get('pcba_package_width') or 0),
                'lenght': float(values.get('pcba_package_length') or 0),
                'thickne': float(values.get('pcba_package_thick') or 0),
                'file_name': '',
                'total': values.get('all_prices').get('cpo_package_cost'),
                'cpo_time': datetime.datetime.now(),
                'bom_type': str(values.get('pcba_material_type') or ''),
                'smt_qty': int(values.get('pcba_package_smt') or 0),
                'dip_qty': int(values.get('pcba_package_dip') or 0),
                'smt_side': values.get('pcba_package_smt_side')
            }
        else:
            order_type = 'PCBA'
            record_data = {
                'order_type': order_type,
                'quantity': int(values.get('cpo_quantity') or 0),
                'width': float(values.get('cpo_width') or 0),
                'lenght': float(values.get('cpo_length') or 0),
                'thickne': float(values.get('pcb_thickness') or 0),
                'file_name': '',
                'total': values.get('all_prices').get('total'),
                'cpo_time': datetime.datetime.now(),
                'bom_type': '',
                'smt_qty': int(values.get('cpo_smt_qty') or 0),
                'dip_qty': int(values.get('cpo_dip_qty') or 0),
                'smt_side': values.get('cpo_side')
            }
        return record_data

    def comparison_time(self, vals, cpo_code):
        """
        去除重复数据，重复数据不保存
        :param vals:
        :return:
        """
        try:
            hours = self.cpo_record_time_setting()
            order_type = vals.get('order_type')
            order_list = ['HDI', 'Rigid-FLex', 'PCB Package', 'PCB']
            format_pattern = "%Y-%m-%d %H:%M:%S"
            datetime_now_utc = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz': 'utc'}),
                                                  fields.Datetime.from_string(fields.Datetime.now())))
            get_time = datetime.datetime.strptime(datetime_now_utc, format_pattern) - datetime.timedelta(hours=hours)
            comparison_time = get_time.strftime(format_pattern)
            if order_type == 'PCB Package':
                if not vals.get('panel_size'):
                    vals['panel_size'] = None
                if not vals.get('item_qty'):
                    vals['item_qty'] = None
            time_domain = [
                ('cpo_time', '>', comparison_time)
            ]

            domain_base = [
                ('order_type', '=', vals.get('order_type')),
                ('quantity', '=', vals.get('quantity')),
                ('width', '=', vals.get('width')),
                ('lenght', '=', vals.get('lenght')),
                ('thickne', '=', vals.get('thickne')),
                ('session_id', '=', vals.get('session_id'))
            ]

            pcb_domain = [
                ('panel_size', '=', vals.get('panel_size')),
                ('item_qty', '=', vals.get('item_qty')),
                ('material', '=', vals.get('material')),
                ('inner_copper', '=', str(vals.get('inner_copper'))),
                ('outer_copper', '=', str(vals.get('outer_copper'))),
                ('layers', '=', vals.get('layers')),
                ('mask_color', '=', vals.get('mask_color')),
                ('silkscreen_color', '=', vals.get('silkscreen_color')),
                ('surface', '=', vals.get('surface')),
                ('e_test', '=', vals.get('e_test'))
            ]

            pcba_domain = [
                ('bom_type', '=', str(vals.get('bom_type'))),
                ('smt_qty', '=', int(vals.get('smt_qty') or 0)),
                ('dip_qty', '=', int(vals.get('dip_qty') or 0)),
                ('smt_side', '=', vals.get('smt_side'))
            ]

            if order_type in order_list:
                self.pcb_and_pcba_record(domain_base+pcb_domain+time_domain, vals, order_type="PCB", cpo_code=cpo_code)
                pcb_pool = request.env['cpo_pcb_record'].sudo()
                records_obj = pcb_pool.search(domain_base+pcb_domain+time_domain)
                if len(records_obj) >= 1:
                    if len(records_obj) == 1:
                        records_obj.cpo_code = cpo_code
                        records_obj.cpo_time = records_obj.create_date
                    else:
                        pass
                else:
                    vals.update({'cpo_code': cpo_code})
                    record_id = pcb_pool.create(vals)
                    return record_id
            else:
                self.pcb_and_pcba_record(domain_base + pcba_domain + time_domain, vals, order_type="PCBA", cpo_code=cpo_code)
                pcb_pool = request.env['cpo_pcba_record'].sudo()
                records_obj = pcb_pool.search(domain_base + pcba_domain + time_domain)
                if len(records_obj) >= 1:
                    if len(records_obj) == 1:
                        records_obj.cpo_code = cpo_code
                        records_obj.cpo_time = records_obj.create_date
                    else:
                        pass
                else:
                    vals.update({'cpo_code': cpo_code})
                    record_id = pcb_pool.create(vals)
                    return record_id
        except Exception, e:
            return False

    def pcb_and_pcba_record(self, all_domain, vals, order_type, cpo_code):
        obj_pool = request.env['cpo_pcb_and_pcba_record'].sudo()
        pcb_and_pcba = obj_pool.search(all_domain)
        values = dict(vals)
        if len(pcb_and_pcba) <= 0:
            if order_type == 'PCB':
                values.update({
                    'bom_type': 0,
                    'smt_qty': 0,
                    'dip_qty': 0,
                    'smt_side': 0
                })
            else:
                values.update({
                    'panel_size': None,
                    'item_qty': None,
                    'material': None,
                    'inner_copper': None,
                    'outer_copper': None,
                    'layers': None,
                    'mask_color': None,
                    'silkscreen_color': None,
                    'surface': None,
                    'e_test': None
                })
            values.update({
                'cpo_code': cpo_code
            })
            obj_pool.create(values)
        else:
            if len(pcb_and_pcba) == 1:
                pcb_and_pcba.cpo_code = cpo_code
                pcb_and_pcba.cpo_time = pcb_and_pcba.create_date
            else:
                pass
        return True

    def cpo_get_user_data(self):
        """
        获取用户信息
        :return:
        """
        data = {}
        get_ip_info = self.add_recode_ip_inf(request, data)
        session_id = request.httprequest.cookies.get('session_id')
        if get_ip_info:
            user_ip_addr = get_ip_info.get('ip')
            if get_ip_info.get('country_name'):
                user_country_name = get_ip_info.get('country_name').encode('utf-8') if get_ip_info.get('country_name') else ''
                user_city_name = get_ip_info.get('city').encode('utf-8') if get_ip_info.get('city') else ''
            else:
                user_country_name = ''
                user_city_name = ''
        else:
            user_ip_addr = ''
            user_country_name = ''
            user_city_name = ''
        session_data = {
            'cpo_country': user_country_name,
            'user_ip': user_ip_addr,
            'session_id': session_id,
            'cpo_city': user_city_name,
        }
        return session_data

    def add_recode_ip_inf(self, request, data):
        """
        获取用户信息
        :param request:
        :param data:
        :return:
        """
        import requests, json
        ip = '127.0.0.1'
        if request.httprequest.environ.get('HTTP_X_REAL_IP'):
            ip = request.httprequest.environ.get('HTTP_X_REAL_IP')
        else:
            ip = request.httprequest.environ.get('REMOTE_ADDR')

        try:
            url = 'https://api.ipdata.co/' + ip + '/zh-CN?api-key=711bdbbbdb292be37d625a22bf9706a435764be5dc8e527322c682c8'
            data = requests.get(url)
            res = json.loads(data.content)
        except Exception, e:
            return {}
        return res

    def cpo_get_user_info(self):
        """
        获取用户信息，作为独立的对象使用
        :return:
        """
        session_id = request.httprequest.cookies.get('session_id')
        user_info = {
            'user_id': request.env.user.id,
            'user_name': request.env.user.name,
            'session_id': session_id
        }
        return user_info

    def get_order_ids_set_quotation_state(self, order_ids, cpo_code):
        try:
            cpo_s_u = self.cpo_get_user_info()
            partner_info = request.env['cpo_session_association'].sudo().check_session_info(cpo_s_u)
            partner_user = {'partner_info': partner_info.get('get_data')}
            session_info = self.cpo_get_user_data()
            user_info = {
                # 'user_id': request.env.user.id,
                'user_name': partner_info.get('get_customer'),
            }
            order_pool = request.env['sale.order'].with_context({'lang':'en_US'}).sudo()
            orders = order_pool.search([('id', 'in', order_ids)])
            for ods in orders:
                if ods.product_id.categ_id.name == 'PCB':
                    record_data = self.order_pcb_quotation_state(ods)
                else:
                    record_data = self.order_pcba_quotation_state(ods)
                all_data = dict(record_data.items() + session_info.items() + user_info.items() + partner_user.items())
                self.comparison_time(all_data, cpo_code)
        except Exception, e:
            pass

        return True

    def order_pcb_quotation_state(self, obj):

        if obj.quotation_line.cpo_hdi != str('0') and obj.quotation_line.cpo_hdi:
            order_type = 'HDI'
        elif obj.quotation_line.soft_number:
            order_type = 'Rigid-FLex'
        elif obj.package_bool:
            order_type = 'PCB Package'
        else:
            order_type = 'PCB'

        # cpo_name = obj.product_id.categ_id.name
        # 金手指和沉金
        # gold_finger = obj.quotation_line.cpo_gold_thick
        # if gold_finger > 0:
        #     finger = "Immersion gold(2u″)" + " Gold finger"
        # else:
        #     finger = ''

        item_number = obj.quotation_line.cpo_item_number
        if item_number > 1:
            pcs_number = obj.quotation_line.pcs_number
            panel_size = item_number
        else:
            pcs_number = ''
            panel_size = ''

        if obj.quotation_line.fly_probe:
            e_test = 'Free Flying Probe'
        else:
            e_test = 'E-test fixture'

        if obj.quotation_line.base_type.name == 'FR4-Tg135-HDI':
            material = 'FR4-Tg135'
        else:
            material = obj.quotation_line.base_type.name

        record_data = {
            'order_type': order_type,
            'quantity': int(obj.order_line.product_uom_qty),
            'width': float(obj.quotation_line.cpo_width),
            'lenght': float(obj.quotation_line.cpo_length),
            'thickne': float(obj.quotation_line.thickness),
            'file_name': '',
            'cpo_time': datetime.datetime.now(),
            'total': obj.amount_total,
            'panel_size': panel_size,
            'item_qty': pcs_number,
            'material': material,
            'inner_copper': float(obj.quotation_line.inner_copper or 0),
            'outer_copper': float(obj.quotation_line.outer_copper or 0),
            'layers': obj.quotation_line.layer_number.layer_number,
            'mask_color': obj.quotation_line.silkscreen_color.english_name,
            'silkscreen_color': obj.quotation_line.text_color.english_name,
            'surface': obj.quotation_line.surface.english_name,
            'e_test': e_test
        }
        return record_data

    def order_pcba_quotation_state(self, obj):
        cpo_name = obj.product_id.categ_id.name
        if obj.package_bool:
            order_type = 'PCBA Package Price'
        else:
            order_type = 'PCBA'
        record_data = {
            'order_type': order_type,
            'quantity': int(obj.order_line.product_uom_qty or 0),
            'width': float(obj.order_line.pcb_width or 0),
            'lenght': float(obj.order_line.pcb_length or 0),
            'thickne': float(obj.order_line.pcb_thickness or 0),
            'file_name': '',
            'total': obj.amount_total,
            'cpo_time': datetime.datetime.now(),
            'bom_type': str(obj.order_line.bom_material_type or ''),
            'smt_qty': int(obj.order_line.smt_component_qty or 0),
            'dip_qty': int(obj.order_line.smt_plug_qty or 0),
            'smt_side': obj.order_line.layer_pcb
        }
        return record_data

    def check_url_record_version(self, type):
        """
        版本管理
        :param type:
        :return:
        """
        check_data = request.env['module_version_management.module_version_setting'].sudo().cpo_view_data_changes(type)
        # check_data = False
        return check_data

    def get_website_source(self):
        """
        获取网站的来源，例如：来自百度，谷歌等
        :return:
        """
        values = {}
        queue_flag = True
        url_index = 0
        try:
            #get_check_data = self.check_url_record_version('url')
            #if not get_check_data:
                #return False
            user_id = request.env.user.id
            user_data = self.cpo_get_user_data()
            cpo_source = request.httprequest.environ.get('HTTP_REFERER')
            if not cpo_source:
                cpo_source = 'https://www.icloudfactory.com'
            access_path = request.httprequest.environ.get('PATH_INFO')
            # 获取用户
            cpo_s_u = self.cpo_get_user_info()
            partner_info = request.env['cpo_session_association'].sudo().check_session_info(cpo_s_u)
            self.check_user_login(cpo_s_u)
            # 判断范文来源
            if request.env.user.name == 'Public user':
                # 当为Public时
                partner_source = request.env['website_cpo_index.cpo_partner_source'].sudo().matching_website(cpo_source)
            else:
                # 普通用户时
                partner_source = request.env['website_cpo_index.cpo_partner_source'].sudo().get_partner_source(user_id, cpo_source)
        except Exception, e:
            _logger.error("postprocess code001: %s value has been dropped (website_source write)" % e)
            return False
        try:
            # 保存同个网址不同参数的网址
            all_source = {
                'site_name': partner_source,
                'cpo_name': cpo_source,
                'session_id': partner_info.get('get_data')
            }
            request.env['website_cpo_index.all_partner_source'].sudo().all_source_data(all_source)
            values.update({
                'user_id': partner_info.get('get_customer'),
                'customer_related': partner_source,
                'cpo_source': cpo_source,
                'access_path': access_path,
                'cpo_ip': user_data.get('user_ip'),
                'cpo_country': user_data.get('cpo_country'),
                'cpo_city': user_data.get('cpo_city'),
                'session_id': partner_info.get('get_data'),
                'cpo_time': fields.Datetime.now(),
            })
            return self.check_source_data(values, cpo_s_u)
        except Exception, e:
            _logger.error("postprocess code002: %s value has been dropped (Create data)" % e)
            return False

    def check_source_data(self, vals, cpo_s_u):
        try:
            web_pool = request.env['website_cpo_index.cpo_website_source'].sudo()
            request_url = request.httprequest.environ['PATH_INFO']
            sess_res = {cpo_s_u.get('session_id'): time.time()}
            web_pool = web_pool.re_cpo_index_session_obj(sess_res, request_url)
            return web_pool.get_data_create({cpo_s_u.get('session_id'): vals}, request_url)
        except Exception, e:
            _logger.error("postprocess code003: %s value has been dropped (more click)" % e)

    def check_user_login(self, cpo_s_u):
        # login_bool = request.params.get('login_success')
        session_association = request.env['cpo_session_association'].sudo()
        # 新增判断
        data_dict = {
            cpo_s_u.get('session_id'): {
                cpo_s_u.get('user_id'): fields.Datetime.now()
            }
        }
        cpo_update = session_association.check_login_data(data_dict)
        if cpo_update:
            # 更新数据
            session_association.update_user_info(cpo_s_u)
            # 删除超时的会话
            session_association.delete_session_time_out()

        # if login_bool:
        #     request.env['cpo_session_association'].sudo().update_user_info(cpo_s_u)




# class SessionData(object):
#
#     def __init__(self):
#         self.session_dict = {}
#         return super(SessionData, self).__init__()
#
#     def init_session_recode(self):
#         s_update = self.session_update()
#         print self.session_dict
#         pass
#
#     def session_update(self):
#         session_id = request.httprequest.cookies.get('session_id').encode('utf-8')
#         cpo_time = datetime.datetime.now()
#         cpo_session = session_id
#         self.check_last_update(cpo_session, cpo_time)
#         self.session_dict[cpo_session] = cpo_time
#
#     def check_last_update(self, cpo_session, time):
#         time_flag = False
#         timedelta = None
#         format_pattern = "%Y-%m-%d %H:%M:%S"
#         datetime_now_utc = fields.Datetime.to_string(
#             fields.Datetime.context_timestamp(request.env.user.with_context({'tz': 'utc'}),
#                                               fields.Datetime.from_string(fields.Datetime.now())))
#         if self.session_dict.get(cpo_session):
#             timedelta = (self.session_dict.get(cpo_session) - time).total_seconds()
#             # timedelta = (datetime.datetime.strptime(datetime_now_utc, format_pattern) -time).total_seconds()
#         print timedelta
#         if timedelta > 160.0:
#             time_flag = True
#         return time_flag







    # def check_session_active(self):
    #     session = request.httprequest['session']
    #     cu_time = time.now()
    #     act_time = cu_time - 5sec
    #     if session not self.session_active.keys():
    #         return True
    #     elif self.session_active[session].get('time') < act_time:
    #         to your api
    #
    # def check_long_time_noupdate(self):
    #     pass
    #
