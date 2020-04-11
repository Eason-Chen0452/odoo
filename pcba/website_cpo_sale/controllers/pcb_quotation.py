# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_cpo_seo.controllers.cpo_setting_seo import Website
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.website_cpo_index.controllers.cpo_quotation_record_code import CpoQuotationRecordCode
import urlparse
from odoo.addons.website.models.website import slug,unslug
import werkzeug
import base64
import logging
import datetime
import json
_logger = logging.getLogger(__name__)

class cpo_electron_WebsiteSale(http.Controller):

    @http.route([
        '/pages/error',
    ], type='http', auth="public", website=True)
    def page_error(self, **post):
        values = {}
        return request.render("website_cpo_sale.pcb_pages_404", values)

    @http.route([
        '/page/quote',
    ], type='http', auth="public", website=True)
    def cpo_page_quote(self, type=None, **post):
        """
        推广网站路由跳转
        :param post:
        :return:
        """
        values = {}
        values.update({
            'pcb_qty': post.get('pcb_qty'),  # 数量
            'pcb_length': post.get('pcb_length'),  # 长度
            'pcb_width': post.get('pcb_width'),  # 宽度
            'layer_number': post.get('layer_number'),  # 层数
            'pcb_thickness': post.get('pcb_thickness'),  # 厚度
            'material_type': post.get('material_type'),  # 基材
            'outer_copper': post.get('outer_copper'),  # 外铜厚
            'inner_copper': post.get('inner_copper'),  # 内铜厚
            'surface_treatment': post.get('surface_treatment'),  # 表面处理
            'solder_mask_color': post.get('solder_mask_color'),  # 阻焊颜色
            'text_color': post.get('text_color'),  # 文字颜色
            'e_test': post.get('e_test'),  # 测试
            'pcb_unit': post.get('pcb_unit'),  # Panel and PCS
            'pcs_qty': post.get('pcs_qty'),  # Panel = n PCS
            'panel_item': post.get('panel_item'),  # Panel contain n item
            'core_thick': post.get('core_thick'),  # material is rogers
            'via_process': post.get('via_process'),  # 过孔处理
            'golden_finger_thickness': post.get('golden_finger_thickness'),  # 金手指金厚
            'immersion_gold_thickness': post.get('immersion_gold_thickness'),  # 沉金金厚
            'dip_through_hole_qty': post.get('dip_through_hole_qty'),  # 后焊孔数
            'smt_parts_qty': post.get('smt_parts_qty'),  # ＳＭＴ贴片个数
            'pcba_special_request': post.get('pcba_special_request'),  # PCBA 特殊要求
            'pcba_other_special_request_content': post.get('pcba_other_special_request_content'),  # PCBA 特殊要求内容
            'pcba_smt': post.get('pcba_smt'),
            'pcba_dip': post.get('pcba_dip'),
            'stencil_thickness': post.get('stencil_thickness'),
            'cpo_stencil_size': post.get('cpo_stencil_size'),
            'pcb_quantity': post.get('pcb_quantity'),
        })
        if not type:
            type = post.get('type')
            if not type:
                return True
        if type == 'pcba':
            return self.pcba_promote_quote(values)
        elif type == 'pcb':
            return self.pcb_promote_quote(values)
        elif type == 'stencil':
            return self.stencil_promote_quote(values)
        return request.redirect("/")

    def pcba_promote_quote(self, vals):
        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcba_electron").product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published': True})
        vals.update({
            'edit': None,
            'order_id': None,
            'product_id': product_tmp_id,
            'pcba_quantity': vals.get('pcb_qty'),
            'pcba_length': vals.get('pcb_length'),
            'pcba_width': vals.get('pcb_width'),
        })
        return request.render("website_cpo_sale.website_smt_standard_template", vals)

    def pcb_promote_quote(self, vals):
        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcb_electron").product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published': True})

        vals.update({
            'edit': None,
            'order_id': None,
            'product_id': product_tmp_id,
            'pcb_quantity': vals.get('pcb_qty'),
            'pcb_layers': vals.get('layer_number'),
        })
        return request.render("website_cpo_sale.website_standard_template", vals)

    def stencil_promote_quote(self, vals):
        product_tmp_id = request.env.ref("cam.cpo_product_template_Stencil").sudo().product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published': True})
        vals.update({
            'edit': None,
            'order_id': None,
            'product_id': product_tmp_id,
        })
        return request.render("website_cpo_sale.stencil_quotaion", vals)



    @http.route([
        '/pcb',
        '/pcb?source=<val>',
    ], type='http', auth="public", website=True)
    def old_pcb(self, login=None, edit=None, source=None, type=None, ufile=None, **post):
        values = {}
        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcb_electron").product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published':True})

        values = {
            'source': source,
            'path': '/pcb',
            'product_id': product_tmp_id,
            'cpo_login': False,
            'edit': edit,
        }
        try:
            # 浏览记录
            CpoQuotationRecordCode().get_website_source()
            # client_user_name = request.env.user.name
            # login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
            # if login_regist:
            #     for lr in login_regist:
            #         lr_boolean = lr.cpo_boolean
            #         if lr_boolean and client_user_name == 'Public user':
            #             values.update({
            #                 'cpo_login': True
            #             })
            #             break
            if login:
                get_user_id = request.env.user.id
                if get_user_id != 4:
                    record_data = self.getQuotationRecord(get_user_id, type)
                    if record_data:
                        values.update({
                            'edit_values': record_data,
                            'login': True
                        })
                    else:
                        values.update({
                            'login': False
                        })
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        keys_arr = post.keys()
        if type:
            if ('pcb_quantity' in keys_arr) or ('pcb_length' in keys_arr) or ('pcb_width' in keys_arr) or ('pcb_layers' in keys_arr) or ('pcb_thickness' in keys_arr):
                values.update({
                    'order_id': None,
                    'pcb_quantity': post.get('pcb_quantity'),
                    'pcb_length': post.get('pcb_length'),
                    'pcb_width': post.get('pcb_width'),
                    'pcb_layers': post.get('pcb_layers'),
                    'pcb_thickness': post.get('pcb_thickness')
                })
            else:
                try:
                    if post.get('order_id'):
                        order_str, get_order_id = unslug(post['order_id'])
                        d_dict = get_order_id
                        if d_dict:
                            # d_dict = werkzeug.url_decode(base64.b64decode(d_list[0]))
                            # if d_dict.get('order_id'):
                            order_id = d_dict
                            pcba_value = request.env['cpo_smt_price.smt'].sudo().get_routine_smt_price(order_id)

                            values.update({
                                'order_id': order_id,
                                'pcb_quantity': int(float(pcba_value.get('cpo_quantity'))),
                                'pcb_length': pcba_value.get('cpo_length'),
                                'pcb_width': pcba_value.get('cpo_width'),
                                # 'pcb_layers': pcba_value.get('pcb_layers'),
                                'pcb_thickness': pcba_value.get('pcb_thickness'),
                                'pcba_fee': pcba_value.get('price'),
                                'pcba_value': pcba_value,
                            })
                except Exception, e:
                    _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)

        values = Website().get_seo_data(values)
        if edit:
            edit_values = self.cpo_edit_pcb_order(edit, type)
            values.update({
                'edit_values': edit_values
            })
        if type:
            if values.get('cpo_login'):
                return request.redirect("/web/login")
            if type == 'standard':
                response = request.render("website_cpo_sale.website_standard_template", values)
            elif type == 'hdi':
                response = request.render("website_cpo_sale.website_pcb_hdi_template", values)
            elif type == 'rigid-flex':
                response = request.render("website_cpo_sale.website_rigid_flex_template", values)
            else:
                response = request.render("website_cpo_sale.website_standard_template", values)
        else:
            response = request.render("website_cpo_sale.pcb_quotation", values)
        quote_signup_history = request.httprequest.cookies.get('quote_signup_history')
        if quote_signup_history:
            response.set_cookie('quote_signup_history', '')
            response.delete_cookie('quote_signup_history')
        return response

    def getQuotationRecord(self, get_user_id, type):
        """
        登录后返回的修改
        :param get_user_id:
        :return:
        """
        file_ids = None
        quote_signup_history = request.httprequest.cookies.get('quote_signup_history')
        if quote_signup_history:
            quote_history = json.loads(quote_signup_history)
            quote_record = request.env['cpo_pcb_record'].sudo().search([('id', '=', quote_history.get('quote_id'))])
        else:
            cpo_cookie = request.httprequest.cookies.get('session_id')
            quote_record = request.env['cpo_pcb_record'].sudo().search([('session_id', '=', cpo_cookie)])
        if not quote_record:
            return False
        quote_data = quote_record[0]
        if quote_data.item_qty:
            unit = 'SET'
            item_qty = int(quote_data.item_qty)
            panel_size = quote_data.panel_size
        else:
            unit = 'PCS'
            item_qty = 0
            panel_size = 0
        special_process = {
            'Semi_hole': quote_data.Semi_hole,
            'Edge_plating': quote_data.Edge_plating,
            'Impedance': quote_data.Impedance,
            'Press_fit': quote_data.Press_fit,
            'Peelable_mask': quote_data.Peelable_mask,
            'Carbon_oil': quote_data.Carbon_oil,
            'min_line_cpo_width': quote_data.Min_line_width,
            'min_hole': quote_data.Min_line_space,
            'min_line_distance': quote_data.Min_aperture,
            'total_holes': quote_data.Total_holes,
            'cpo_hole_copper': quote_data.Copper_weight_wall,
            'cpo_core_number': quote_data.Number_core,
            'cpo_pp_number': quote_data.PP_number,
            'test_points': quote_data.Total_test_points,
            'Blind_and_buried_hole': quote_data.Blind_and_buried_hole,
            'Blind_hole_structure': quote_data.Blind_hole_structure,
            'Depth_control_routing': quote_data.Depth_control_routing,
            'Number_back_drilling': quote_data.Number_back_drilling,
            'Countersunk_deep_holes': quote_data.Countersunk_deep_holes,
            'Laser_drilling': quote_data.Laser_drilling,
            'line_to_hole_distance': quote_data.Inner_hole_line,
            'The_space_for_drop_V_cut': quote_data.The_space_for_drop_V_cut,
        }
        hdi = {
            'cpo_hdi': 1,
        }

        rigid_flex = {
            'soft_level': 'Inner layer',
            'window_bool': 'Outer layer',
            'soft_number': quote_data.flex_number,
        }
        base_type = quote_data.material
        if 'Rogers' in base_type:
            material = base_type.split(' ')[0]
            material_val = base_type.split(' ')[1]
        else:
            material = base_type.split('-')[0]
            material_val = base_type.split('-')[1]
        if quote_data.file_ids:
            file_ids = quote_data.file_ids
        edit_values = {
            'login': True,
            'cpo_standard': 2,
            'pcb_qty': quote_data.quantity,
            'layer_number': int(quote_data.layers),
            'cpo_length': quote_data.lenght,
            'cpo_width': quote_data.width,
            'base_type': quote_data.material,
            'thickness': quote_data.thickne,
            'surface': quote_data.surface,
            'surface_left': quote_data.surface.split('+')[0],
            'outer_copper': float(quote_data.outer_copper),
            'inner_copper': float(quote_data.inner_copper),
            'silkscreen_color': quote_data.mask_color,  # 阻焊颜色
            'text_color': quote_data.silkscreen_color,  # 文字颜色
            'fly_probe': quote_data.e_test,
            'material': material,  # 基材
            'material_val': material_val,  # 基材型号
            'core_thick': '12',  # 罗杰斯芯板厚度
            'unit': unit,  # 单位
            'pcb_splice': item_qty,  # 拼板款数：1 * （pcs_per_set） PCS
            'cpo_item_number': panel_size,  # 拼板款数：1 * （pcs_per_set） PCS
            'via_process': 'Opening',  # 过控工艺
            'cpo_gold_thick': quote_data.golden_finger_thickness,  # 金手指金厚
            'immersion_gold_thickness': 0,  # 沉金金厚
            'special_process': special_process,  # 特殊数据
            'hdi': hdi,  # HDI
            'rigid_flex': rigid_flex,  # 软硬结合
            'ir_file_ids': file_ids,  #
        }
        return edit_values

    def cpo_edit_pcb_order(self, edit, type):
        """
        购物车数据更改
        :param edit:
        :param type:
        :return:
        """
        special_process, hdi, rigid_flex, sp_data, sp_data2, spe_data3 = None, None, None, {}, {}, {}
        order_id = base64.b64decode(edit[5:]).decode()
        partner_id = request.env.user.partner_id.id
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id), ('partner_id', '=', partner_id)])
        # 特殊工艺
        spe_data = sale_order.quotation_line.sprocess_ids
        spe_data2 = sale_order.quotation_line.smaterial_ids
        if spe_data:
            sp_data = self.getSpecialAnayci(spe_data)
        if spe_data2:
            for x in spe_data2:
                x_name = x.english_name
                if 'Carbon_oil' in x_name:
                    sp_data2.update({
                        'Carbon_oil': 'Yes',
                    })
                if 'Peelable_mask' in x_name:
                    sp_data2.update({
                        'Peelable_mask': 'Yes',
                    })

        if sale_order.quotation_line.drilling:
            spe_data3.update({
                'Laser_drilling': 'Yes',
            })
        if sale_order.quotation_line.v_cut:
            spe_data3.update({
                'The_space_for_drop_V_cut': 'Yes',
            })
        if sale_order.quotation_line.back:
            spe_data3.update({
                'Number_back_drilling': 'Yes',
            })

        special_process = {
            # 'test_points': sale_order.quotation_line.test_points,  # 测试点
            # 'min_hole': sale_order.quotation_line.min_hole,  # 最小孔
            # 'min_line_cpo_width': sale_order.quotation_line.min_line_cpo_width,  # 最小线宽
            # 'min_line_distance': sale_order.quotation_line.min_line_distance,  # 最小线距
            # 'line_to_hole_distance': sale_order.quotation_line.line_to_hole_distance,  # 内层孔到线
            # 'total_holes': sale_order.quotation_line.total_holes,  # 总孔数
            # 'cpo_pp_number': sale_order.quotation_line.cpo_pp_number,  # PP 张数
            # 'cpo_core_number': sale_order.quotation_line.cpo_core_number,  # 芯板张数
            # 'cpo_hole_copper': sale_order.quotation_line.cpo_hole_copper,  # 孔铜

            'Semi_hole': sp_data.get('Semi_hole', 'No'),
            'Edge_plating': sp_data.get('Edge_plating', 'No'),
            'Impedance': sp_data.get('Impedance', 'No'),
            'Press_fit': sp_data.get('Press_fit', 'No'),
            'Peelable_mask': sp_data2.get('Peelable_mask', 'No'),
            'Carbon_oil': sp_data2.get('Carbon_oil', 'No'),
            'min_line_cpo_width': str(sale_order.quotation_line.min_line_cpo_width),  # 最小线宽
            'min_hole': str(sale_order.quotation_line.min_hole),  # 最小孔
            'min_line_distance': str(sale_order.quotation_line.min_line_distance),  # 最小线距
            'total_holes': str(sale_order.quotation_line.total_holes),
            'cpo_hole_copper': str(sale_order.quotation_line.cpo_hole_copper),  # 孔铜
            'cpo_core_number': str(sale_order.quotation_line.cpo_core_number),  # 芯板张数
            'cpo_pp_number': str(sale_order.quotation_line.cpo_pp_number),  # PP 张数
            'test_points': str(sale_order.quotation_line.test_points),  # 测试点
            'Blind_and_buried_hole': sp_data.get('Blind_and_buried_hole', '0'),
            'Blind_hole_structure': sp_data.get('Blind_hole_structure', '0'),
            'Depth_control_routing': sp_data.get('Depth_control_routing', '0'),
            'Number_back_drilling': spe_data3.get('Number_back_drilling', 'No'),
            'Countersunk_deep_holes': sp_data.get('Press_fit', '0'),
            'Laser_drilling': spe_data3.get('Laser_drilling', 'No'),
            'line_to_hole_distance': str(sale_order.quotation_line.line_to_hole_distance),  # 内层孔到线
            'The_space_for_drop_V_cut': spe_data3.get('The_space_for_drop_V_cut', 'No'),
        }
        # HDI
        if type == 'hdi':
            hdi = {
                'cpo_hdi': int(sale_order.quotation_line.cpo_hdi),
            }
        if type == 'rigid-flex':
            rigid_flex = {
                'soft_level': sale_order.quotation_line.soft_level,
                'window_bool': sale_order.quotation_line.window_bool,
                'soft_number': sale_order.quotation_line.soft_number,
            }
        base_type = sale_order.quotation_line.base_type.english_name
        if 'Rogers' in base_type:
            material = base_type.split(' ')[0]
            material_val = base_type.split(' ')[1]
        else:
            material = base_type.split('-')[0]
            material_val = base_type.split('-')[1]
        # 标准工艺
        edit_values = {
            'edit_id': order_id,
            'cpo_standard': sale_order.quotation_line.cpo_standard.english_name,
            'pcb_qty': sale_order.quotation_line.product_uom_qty,
            'layer_number': sale_order.quotation_line.layer_number.layer_number,
            'cpo_length': sale_order.quotation_line.cpo_length,
            'cpo_width': sale_order.quotation_line.cpo_width,
            'base_type': base_type,
            'thickness': sale_order.quotation_line.thickness,
            'surface': sale_order.quotation_line.surface.english_name,
            'surface_left': None,
            'outer_copper': sale_order.quotation_line.outer_copper,
            'inner_copper': sale_order.quotation_line.inner_copper,
            'silkscreen_color': sale_order.quotation_line.silkscreen_color.english_name,  # 阻焊颜色
            'text_color': sale_order.quotation_line.text_color.english_name,  # 文字颜色
            'fly_probe': sale_order.quotation_line.fly_probe,
            'material': material,  # 基材
            'material_val': material_val,  # 基材型号
            'core_thick': sale_order.quotation_line.core_thick,  # 罗杰斯芯板厚度
            'unit': sale_order.quotation_line.product_uom.name,  # 单位
            'pcb_splice': sale_order.quotation_line.pcs_per_set,  # 拼板款数：1 * （pcs_per_set） PCS
            'cpo_item_number': sale_order.quotation_line.cpo_item_number,  # 拼板款数：1 * （pcs_per_set） PCS
            'via_process': sale_order.quotation_line.via_process.english_name,  # 过控工艺
            'cpo_gold_thick': sale_order.quotation_line.cpo_gold_thick,  # 金手指金厚
            'immersion_gold_thickness': sale_order.quotation_line.gold_thickness,  # 沉金金厚
            'special_process': special_process,  # 特殊数据
            'hdi': hdi,  # HDI
            'rigid_flex': rigid_flex,  # 软硬结合
            'ir_file_ids': None,  # 软硬结合
        }

        return edit_values

    def getSpecialAnayci(self, spe_data):
        """
        解析特殊数据
        :param spe_data:
        :return:
        """
        sp_data = {}
        for x in spe_data:
            x_name = x.english_name
            if x_name in 'Semi-hole':
                sp_data.update({
                    'Semi_hole': 'Yes',
                })
            if 'Number of countersunk' in x_name:
                sp_data.update({
                    'Countersunk_deep_holes': 'Yes',
                })
            if 'Edge Plating' in x_name:
                sp_data.update({
                    'Edge_plating': 'Yes',
                })
            if 'Depth control routing' in x_name:
                sp_data.update({
                    'Depth_control_routing': 'Yes',
                })
            if 'Press-fit' in x_name:
                sp_data.update({
                    'Press_fit': 'Yes',
                })
            if 'Impendance' in x_name:
                sp_data.update({
                    'Impedance': 'Yes',
                })
            if 'Blind hole structure' in x_name:
                sp_data.update({
                    'Blind_hole_structure': 'Yes',
                })
            if 'Blind&Buired via' in x_name:
                sp_data.update({
                    'Blind_and_buried_hole': 'Yes',
                })
        return sp_data

    def getQuoteRecordId(self):
        """
        获取报价记录的第一条
        :return:
        """
        cpo_cookie = request.httprequest.cookies.get('session_id')
        quote_record = request.env['cpo_pcb_record'].sudo().search([('session_id', '=', cpo_cookie)])
        if not quote_record:
            return False
        quote_data = quote_record[0]
        return quote_data.id

    @http.route([
        '/get/record/id',
    ], type='json', auth="public", website=True)
    def getQuoteRecordInPCB(self, **kw):
        quote_id = self.getQuoteRecordId()
        if quote_id:
            kw.update({
                'quote_id': quote_id.id
            })
            return kw
        else:
            kw.update({
                'quote_id': None
            })
            return kw

    @http.route([
        '/pcb/package-price',
    ], type="http", auth="public", website=True)
    def pcb_packge_price(self, login=None, type=None, edit=None, **kw):
        """
        PCB 打包价
        :return:
        """
        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcb_electron").product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published': True})

        values = {
            'product_id': product_tmp_id,
            'cpo_login': False,
            'edit': edit,
        }
        try:
            CpoQuotationRecordCode().get_website_source()
            if login:
                get_user_id = request.env.user.id
                if get_user_id != 4:
                    record_data = self.getQuotationRecord(get_user_id, type)
                    if not record_data:
                        values.update({
                            'edit_values': record_data,
                            'login': False
                        })
                    else:
                        values.update({
                            'edit_values': record_data,
                            'login': True
                        })
            # client_user_name = request.env.user.name
            # login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
            # if login_regist:
            #     for lr in login_regist:
            #         lr_boolean = lr.cpo_boolean
            #         if lr_boolean and client_user_name == 'Public user':
            #             values.update({
            #                 'cpo_login': True
            #             })
            #         break
            # if values.get('cpo_login'):
            #     return request.redirect("/web/login")
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        if edit:
            edit_values = self.cpo_edit_order(edit)
            values.update({
                'edit': edit,
                'edit_values': edit_values,
            })
        return request.render("website_cpo_sale.website_pcb_package_price", values)

    def cpo_edit_order(self, edit):
        """
        处理客户更改数据问题
        类型：PCB 打包价
        :param edit:
        :return:
        """
        order_id = base64.b64decode(edit[5:]).decode()
        partner_id = request.env.user.partner_id.id
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id), ('partner_id', '=', partner_id)])
        edit_values = {
            'edit_id': order_id,
            'cpo_standard': sale_order.quotation_line.cpo_standard.english_name,
            'pcb_qty': sale_order.order_line.product_uom_qty,
            'layer_number': sale_order.quotation_line.layer_number.layer_number,
            'cpo_length': sale_order.quotation_line.cpo_length,
            'cpo_width': sale_order.quotation_line.cpo_width,
            'base_type': sale_order.quotation_line.base_type.english_name,
            'thickness': sale_order.quotation_line.thickness,
            'surface': sale_order.quotation_line.surface.english_name,
            'outer_copper': sale_order.quotation_line.outer_copper,
            'inner_copper': sale_order.quotation_line.inner_copper,
            'silkscreen_color': sale_order.quotation_line.silkscreen_color.english_name,
            'text_color': sale_order.quotation_line.text_color.english_name,
            'fly_probe': 'Free Flying Probe',
        }
        return edit_values

    # PCB 打包价
    @http.route([
        '/cpo_pcbpackage_quotation',
    ], type='json', auth="public", website=True)
    def cpo_pcbpackage_quotation(self, **post):
        """
        PCB Package Price
        :param post:
        :return:
        """
        try:
            pcb_sale_quotation = request.env['sale.quotation'].sudo()
            pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post, package=True)
            if pcb_quotation.get('warning'):
                post['error'] = pcb_quotation.get('warning')
            else:
                post['pcb_package'] = pcb_quotation
                post['package'] = True
                value = pcb_quotation['value']
                # if value['pcb_special']:
                    # post['pcb_special_requirements']['Total_holes'] = value['pcb_special']['Total_holes']
                    # post['pcb_special_requirements']['Inner_hole_line'] = value['pcb_special']['Inner_hole_line']
                    # post['pcb_special_requirements']['Number_core'] = value['pcb_special']['Number_core']
                    # post['pcb_special_requirements']['PP_number'] = value['pcb_special']['PP_number']
                    # post['pcb_special_requirements']['Blind_hole_structure'] = value['pcb_special']['Blind_hole_structure']
                    # post['pcb_special_requirements']['Blind_and_buried_hole'] = value['pcb_special']['Blind_and_buried_hole']
                    # post['pcb_special_requirements']['Min_line_width'] = value['pcb_special']['Min_line_width']
                    # post['pcb_special_requirements']['Min_line_space'] = value['pcb_special']['Min_line_space']
                    # post['pcb_special_requirements']['Min_aperture'] = value['pcb_special']['Min_aperture']
                    # post['pcb_special_requirements']['Copper_weight_wall'] = value['pcb_special']['Copper_weight_wall']
                    # post['pcb_special_requirements']['Countersunk_deep_holes'] = value['pcb_special']['Countersunk_deep_holes']
                    # post['pcb_special_requirements']['Total_test_points'] = value['pcb_special']['Total_test_points']
                # 检查用户是否登录
                cpo_login = self.check_user_login()
                if cpo_login:
                    source = request.httprequest.environ.get('HTTP_REFERER')
                    url = self.analysis_url(source)
                    cpo_url = self.analysis_url_return_data(source)
                    post.update({
                        'login': 'please log in first!',
                        'url': url,
                        'src': cpo_url.get('src'),
                        'type': cpo_url.get('type'),
                    })
                    return post
        except Exception, e:
            post['error'] = {
                'e': e
            }
        return post

    @http.route('/blind/structure', type='json', auth='public', website=True)
    def enter_blind_structure(self, **post):
        """
        客户输入钻带数，判断钻带数和埋盲孔
        :param post:
        :return:
        """
        # 以下数据使用后可以删除
        # 'blind_structure' 钻带数
        # 'layer' 层数
        sale_quotation = request.env['sale.quotation'].sudo()
        hdi_val = sale_quotation.check_layer_blind_number(post)

        # print hdi_val
        post['hdi_return'] = hdi_val
        return post

    def analysis_url(self, url):
        """
        URL解析，返回路径
        :param url:
        :return:
        """
        cpo_url = None
        analysis = urlparse.urlsplit(url)
        if analysis.query:
            cpo_url = 'src='+analysis.path + '&' + analysis.query
        else:
            cpo_url = 'src='+analysis.path
        return cpo_url

    def analysis_url_return_data(self, url):
        """
        URL解析，返回对象
        :param url:
        :return:
        """
        vals = {}
        analysis = urlparse.urlsplit(url)
        if '&' in analysis.query:
            an_data = analysis.query.split('&')
            for a in an_data:
                ty_data = a.split('=')
                if ty_data[0] == 'type':
                    vals.update({
                        'src': analysis.path,
                        'type': ty_data[1],
                    })
                    break
        ty_data = analysis.query.split('=')
        if ty_data[0] == 'type':
            vals.update({
                'src': analysis.path,
                'type': ty_data[1],
            })
        return vals

    def check_user_login(self):
        """
        检查用户是否登录，强制用户登录接口
        时间：2019年12月10日14:05:57
        :return:
        """
        cpo_login = False
        client_user_name = request.env.user.name
        login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
        if login_regist:
            for lr in login_regist:
                lr_boolean = lr.cpo_boolean
                if lr_boolean and client_user_name == 'Public user':
                    cpo_login = True
                    break
        return cpo_login

    @http.route('/cpo/login', type='json', auth="public", website=True)
    def quote_login_and_signup(self, **kw):
        """
        在报价页面弹出登录框
        :param kw:
        :return:
        """
        # 检查用户是否登录
        cpo_login = self.check_user_login()
        if cpo_login:
            source = request.httprequest.environ.get('HTTP_REFERER')
            url = self.analysis_url(source)
            cpo_url = self.analysis_url_return_data(source)
            # kw['login'] = 'please log in first!'
            # kw['url'] = '/web/login?' + cpo_url
            kw.update({
                'login': 'please log in first!',
                'url': url,
                'src': cpo_url.get('src'),
                'type': cpo_url.get('type'),
            })
            return kw
        kw['login'] = None
        return kw

    @http.route('/get/hdi', type='json', auth="public", website=True)
    def cpoGetHdi(self, **post):
        """
        HDI, 点击报价接口：数据传入
        :param post:
        :return:
        """
        try:
            sale_quotation = request.env['sale.quotation'].sudo()
            hdi_quotation = sale_quotation.get_pcb_quotation_price(post, package=False)
            # 检查用户是否登录
            cpo_login = self.check_user_login()
            if cpo_login:
                source = request.httprequest.environ.get('HTTP_REFERER')
                url = self.analysis_url(source)
                # post['login'] = 'please log in first!'
                # post['url'] = '/web/login?' + cpo_url
                cpo_url = self.analysis_url_return_data(source)
                quote_id = self.getQuoteRecordId()
                post.update({
                    'login': 'please log in first!',
                    'url': url,
                    'src': cpo_url.get('src'),
                    'type': cpo_url.get('type'),
                    'quote_id': quote_id,
                    'hdi_quotation': hdi_quotation,
                })
                return post
            if hdi_quotation.get('warning'):
                post['error'] = hdi_quotation.get('warning')
            else:
                cost_data = hdi_quotation.get('value')
                pcb_price_detailed = {}
                if cost_data:
                    pcb_price_detailed.update({
                        'Special Process Cost': cost_data['Special Process Cost'],  # 特殊工艺费 spe_precess
                        'Cost By': cost_data['Cost By'],
                        'Thickness Cost': cost_data['Thickness Cost'],
                        'Copper Cost': cost_data['Copper Cost'],
                        'Text Color Cost': cost_data['Text Color Cost'],
                        'Solder Mask Color Cost': cost_data['Solder Mask Color Cost'],
                        'Surface Cost': cost_data['Surface Cost'],
                        'Core&PP Cost': cost_data['Core&PP Cost'],
                        'Other Cost': cost_data['Other Cost'],
                        'Gold Finger Cost': cost_data['Gold Finger Cost'],
                        'Special Material Cost': cost_data['Special Material Cost']
                    })
                    if cost_data.get('pcb_special'):
                        pcb_special_data = cost_data.get('pcb_special')
                        # post['pcb_special_requirements']['Total_holes'] = pcb_special_data.get('Total_holes')
                        # post['pcb_special_requirements']['Inner_hole_line'] = pcb_special_data.get('Inner_hole_line')
                        # post['pcb_special_requirements']['Number_core'] = pcb_special_data.get('Number_core')
                        # post['pcb_special_requirements']['PP_number'] = pcb_special_data.get('PP_number')
                        # post['pcb_special_requirements']['Blind_hole_structure'] = pcb_special_data.get('Blind_hole_structure')
                        # post['pcb_special_requirements']['Blind_and_buried_hole'] = pcb_special_data.get('Blind_and_buried_hole')
                        # post['pcb_special_requirements']['Min_line_width'] = pcb_special_data.get('Min_line_width')
                        # post['pcb_special_requirements']['Min_line_space'] = pcb_special_data.get('Min_line_space')
                        # post['pcb_special_requirements']['Min_aperture'] = pcb_special_data.get('Min_aperture')
                        # post['pcb_special_requirements']['Copper_weight_wall'] = pcb_special_data.get('Copper_weight_wall')
                        # post['pcb_special_requirements']['Countersunk_deep_holes'] = pcb_special_data.get('Countersunk_deep_holes')
                        # post['pcb_special_requirements']['Total_test_points'] = pcb_special_data.get('Total_test_points')
                post.update({
                    'pcb_price_detailed': pcb_price_detailed,
                    'hdi_quotation': hdi_quotation,
                })
        except Exception, e:
            post['error'] = {
                'e': e
            }
        return post

    @http.route('/flex-rigid', type='json', auth="public", website=True)
    def cpoFlexRigid(self, **post):
        """
        Flex-Rigid 点击报价接口：数据传入
        :param post:
        :return:
        """
        try:
            sale_quotation = request.env['sale.quotation'].sudo()
            flex_rigid_quotation = sale_quotation.get_pcb_quotation_price(post, package=False)
            # 检查用户是否登录
            cpo_login = self.check_user_login()
            if cpo_login:
                source = request.httprequest.environ.get('HTTP_REFERER')
                url = self.analysis_url(source)
                # post['login'] = 'please log in first!'
                # post['url'] = '/web/login?' + cpo_url
                cpo_url = self.analysis_url_return_data(source)
                quote_id = self.getQuoteRecordId()
                post.update({
                    'login': 'please log in first!',
                    'url': url,
                    'src': cpo_url.get('src'),
                    'type': cpo_url.get('type'),
                    'quote_id': quote_id,
                    'value': flex_rigid_quotation,
                })
                return post
            if flex_rigid_quotation.get('warning'):
                post['error'] = flex_rigid_quotation.get('warning')
            else:
                pcb_price_detailed = {}
                flex_rigid_data = flex_rigid_quotation.get('value')
                pcb_price_detailed.update({
                    'Special Process Cost': flex_rigid_data['Special Process Cost'],  # 特殊工艺费 spe_precess
                    'Cost By': flex_rigid_data['Cost By'],
                    'Thickness Cost': flex_rigid_data['Thickness Cost'],
                    'Copper Cost': flex_rigid_data['Copper Cost'],
                    'Text Color Cost': flex_rigid_data['Text Color Cost'],
                    'Solder Mask Color Cost': flex_rigid_data['Solder Mask Color Cost'],
                    'Surface Cost': flex_rigid_data['Surface Cost'],
                    'Core&PP Cost': flex_rigid_data['Core&PP Cost'],
                    'Other Cost': flex_rigid_data['Other Cost'],
                    'Gold Finger Cost': flex_rigid_data['Gold Finger Cost'],
                    'Special Material Cost': flex_rigid_data['Special Material Cost']
                })
                if flex_rigid_data.get('pcb_special'):
                    flex_rigid = flex_rigid_data.get('pcb_special')
                    # post['pcb_special_requirements']['Total_holes'] = flex_rigid.get('Total_holes')
                    # post['pcb_special_requirements']['Inner_hole_line'] = flex_rigid.get('Inner_hole_line')
                    # post['pcb_special_requirements']['Number_core'] = flex_rigid.get('Number_core')
                    # post['pcb_special_requirements']['PP_number'] = flex_rigid.get('PP_number')
                    # post['pcb_special_requirements']['Blind_hole_structure'] = flex_rigid.get('Blind_hole_structure')
                    # post['pcb_special_requirements']['Blind_and_buried_hole'] = flex_rigid.get('Blind_and_buried_hole')
                    # post['pcb_special_requirements']['Min_line_width'] = flex_rigid.get('Min_line_width')
                    # post['pcb_special_requirements']['Min_line_space'] = flex_rigid.get('Min_line_space')
                    # post['pcb_special_requirements']['Min_aperture'] = flex_rigid.get('Min_aperture')
                    # post['pcb_special_requirements']['Copper_weight_wall'] = flex_rigid.get('Copper_weight_wall')
                    # post['pcb_special_requirements']['Countersunk_deep_holes'] = flex_rigid.get('Countersunk_deep_holes')
                    # post['pcb_special_requirements']['Total_test_points'] = flex_rigid.get('Total_test_points')
                post.update({
                    'value': flex_rigid_quotation,
                    'pcb_price_detailed': pcb_price_detailed,
                    'flex_layers': flex_rigid_quotation.get('Total Layer')
                })
        except Exception, e:
            post['error'] = {
                'e': e
            }
        return post

    def cpoRecordDateGet(self, user_id, type):
        """
        PCBA 报价跳转登录，返回数据
        :param _user_id:
        :param type:
        :return:
        """
        cpo_cookie = request.httprequest.cookies.get('session_id')
        quote_record = None
        quote_record = request.env['cpo_pcba_record'].sudo().search([('session_id', '=', cpo_cookie)])
        if not quote_record:
            return False
        edit_values = {
            'product_uom_qty': quote_record.quantity,
            'pcb_length': quote_record.lenght,
            'pcb_width': quote_record.width,
            'smt_plug_qty': quote_record.dip_qty,
            'smt_component_qty': quote_record.smt_qty,
            'layer_pcb': int(quote_record.smt_side),
            'pcb_thickness': quote_record.thickne,
            'pcb_special': 'No',
            'surface_id': 'Lead Free HASL',  # 表名处理
            'cpo_note': None,
            'bom_material_type': quote_record.bom_type,  # BOM 物料种类
            'quote_line': 0,
        }
        return edit_values

    #  PCBA 打包价
    @http.route('/pcba/package-price', type="http", auth="public", website=True)
    def pcba_packge_price(self):
        """
        PCBA 打包价
        :return:
        """
        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcba_electron").product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published': True})

        values = {
            'product_id': product_tmp_id,
        }
        return request.render("website_cpo_sale.website_pcba_package_price", values)

    # PCBA 打包价计算
    @http.route([
        '/pcba-package-price',
    ], type='json', auth="public", website=True)
    def cpo_pcba_package_quotation(self, **post):
        """
        PCBA Package Price calculation
        :param post:
        :return:
        """
        try:
            pcba_package_quotation = request.env['sale.order'].sudo()
            pcba_package = pcba_package_quotation.get_smt_package(post, package=True)
            post['pcba_package'] = pcba_package
            post['warning'] = pcba_package.get('warning')
            # 检查用户是否登录
            cpo_login = self.check_user_login()
            if cpo_login:
                source = request.httprequest.environ.get('HTTP_REFERER')
                url = self.analysis_url(source)
                # post['login'] = 'please log in first!'
                # post['url'] = '/web/login?' + cpo_url
                cpo_url = self.analysis_url_return_data(source)
                quote_id = self.getQuoteRecordId()
                post.update({
                    'login': 'please log in first!',
                    'url': url,
                    'src': cpo_url.get('src'),
                    'type': cpo_url.get('type'),
                    'quote_id': quote_id,
                })
                return post
        except Exception, e:
            post['error'] = {
                'e': e
            }
        return post

    @http.route('/po/number', type="json", auth="public", website=True)
    def set_po_number(self, **kw):
        """
        添加PO号
        :param kw:
        :return:
        """
        values = kw.get('vals')
        if not values.get('order_id'):
            values['error'] = 'Please refresh and try again!'
            return values
        if not values.get('po_number'):
            values['error'] = 'Please fill in the PO number!'
            return values
        order = request.env['sale.order'].sudo().search([('id', '=', values.get('order_id'))])
        order.update({
            'po_number': values.get('po_number')
        })
        return values

    @http.route('/part/number', type="json", auth="public", website=True)
    def set_part_number(self, **kw):
        """
        添加Part No.
        :param kw:
        :return:
        """
        values = kw.get('vals')
        if not values.get('order_id'):
            values['error'] = 'Please refresh and try again!'
            return values
        if not values.get('part_no'):
            values['error'] = 'Please fill in the PO number!'
            return values
        order = request.env['sale.order'].sudo().search([('id', '=', values.get('order_id'))])
        order.update({
            'part_no': values.get('part_no')
        })
        return values

    @http.route('/quote/check/login', type="json", auth="public", website=True)
    def cpo_quote_check_login(self, **kw):
        # 检查用户是否登录
        cpo_login = self.check_user_login()
        if cpo_login:
            source = request.httprequest.environ.get('HTTP_REFERER')
            url = self.analysis_url(source)
            cpo_url = self.analysis_url_return_data(source)
            quote_id = self.getQuoteRecordId()
            kw.update({
                'login': 'please log in first!',
                'url': url,
                'src': cpo_url.get('src'),
                'type': cpo_url.get('type'),
                'quote_id': quote_id,
            })
            return kw
        return None

    @http.route('/create/special/order', type="json", auth="public", website=True)
    def cpo_create_special_order(self, **kw):
        """
        当网页报价无法满足时，提供人工审核单
        :param kw:
        :return:
        """
        try:
            values, package, x_id = {}, False, None
            pcb_value = kw.get('pcb_value')
            cpohdi = kw.get('cpohdi')
            soft_hard = kw.get('soft_hard')
            file_names = kw.get('file_names')
            pcb_surfaces = pcb_value.get('pcb_surfaces')
            psr = kw.get('pcb_special_requirements')
            if psr:
                for k,v in psr.items():
                    values.update({
                        k: v,
                    })
            values.update({
                'pcb_user_name': request.env.user.name,
                'pcb_user_id': request.env.user.id,
                'pcb_partner_id': request.env.user.partner_id.id,
                'pcb_surfaces': {
                    'pcb_surface': pcb_surfaces.get('surface_value'),
                    'gold_finger_thickness': pcb_surfaces.get('gold_finger_thickness'),
                    'gold_finger_width': pcb_surfaces.get('gold_finger_width'),
                    'gold_finger_length': pcb_surfaces.get('gold_finger_length'),
                    'gold_finger_qty': pcb_surfaces.get('gold_finger_qty'),
                    'coated_area': pcb_surfaces.get('coated_area'),
                    'nickel_thickness': pcb_surfaces.get('nickel_thickness'),
                }
            })
            # Rogers
            if pcb_value.get('core_thick'):
                values.update({
                    'pcb_rogers': {
                        'core_thick': kw.get('core_thick'),
                        'rogers_number': kw.get('rogers_number')
                    }
                })
            # HDI
            if cpohdi.get('number_of_step'):
                values.update({
                    'pcb_hdi': {
                        'number_of_step': cpohdi.get('number_of_step')
                    }
                })
            # flex-rigit
            if soft_hard.get('cpo_flex_number'):
                values.update({
                        'pcb_soft_hard': {
                            'cpo_inner_outer': soft_hard.get('cpo_inner_outer'),
                            'cpo_flex_open': soft_hard.get('cpo_flex_open'),
                            'cpo_flex_number': soft_hard.get('cpo_flex_number'),
                            'cpo_flex_connect_len': soft_hard.get('cpo_flex_connect_len'),
                        }
                })
            values.update({
                'cpo_quantity': pcb_value.get('cpo_quantity'),  # PCBA 数量
                'pcb_qty': pcb_value.get('pcb_qty'),  # PCB 数量
                'cpo_side': pcb_value.get('cpo_side'),  # PCBA 单双面贴片
                'cpo_smt_qty': pcb_value.get('cpo_smt_qty'),  # smt 个数
                'bom_id': pcb_value.get('bom_id'),
                'cpo_dip_qty': pcb_value.get('cpo_dip_qty'),  # DIP 数量
                'cpo_components_supply': pcb_value.get('cpo_components_supply'),  # BOM 供货方式
                'cpo_pcb_supply': pcb_value.get('cpo_pcb_supply'),  # PCB 供货方式
                'cpo_length': pcb_value.get('cpo_length'),  # PCBA and PCBA 共用字段，长度
                'cpo_width': pcb_value.get('cpo_width'),  ## PCBA and PCBA 共用字段，宽度
                'pcb_thickness': pcb_value.get('pcb_thickness'),  # PCBA 板厚
                'cpo_select_value': pcb_value.get('cpo_select_value'),  # PCBA 特殊要求
                'quality_standard': pcb_value.get('quality_standard'),  # 验收标准
                'pcb_qty_unit': pcb_value.get('pcb_qty_unit'),  # PCB 单位（是否拼版）
                'pcb_width': pcb_value.get('pcb_breadth'),  # pcb宽度
                'pcb_length': pcb_value.get('pcb_length'),  # pcb长度
                'pcb_pcs_size': pcb_value.get('pcb_pcs_size'),  # Panl
                'pcb_item_size': pcb_value.get('pcb_item_size'),  # Item
                'gold_finger_thickness': pcb_value.get('gold_finger_thickness'),
                'gold_finger_width': pcb_value.get('gold_finger_width'),
                'gold_finger_length': pcb_value.get('gold_finger_length'),
                'gold_finger_qty': pcb_value.get('gold_finger_qty'),
                'coated_area': pcb_value.get('coated_area'),
                'nickel_thickness': pcb_value.get('nickel_thickness'),
                'pcb_quotation_area':  pcb_value.get('pcb_quotation_area'),  #
                'pcb_layer': pcb_value.get('pcb_layer'),  # 层数
                'pcb_type': pcb_value.get('pcb_type'),  # 材料型号
                'pcb_thickness': pcb_value.get('pcb_thickness'),  # 板厚
                'pcb_inner_copper': pcb_value.get('pcb_inner_copper'),  # 内铜厚
                'pcb_outer_copper': pcb_value.get('pcb_outer_copper'),  # 外铜厚
                'pcb_solder_mask': pcb_value.get('pcb_solder_mask'),  #
                'pcb_silkscreen_color': pcb_value.get('pcb_silkscreen_color'),
                'pcb_vias': pcb_value.get('pcb_vias'),
                'cpo_pcb_frame': pcb_value.get('cpo_pcb_frame'),
                'pcb_test': pcb_value.get('pcb_test'),
            })

            # if kwargs.get('pcb_surface'):
            #     values['pcb_surface'] = kwargs.get('pcb_surface')
            # else:
            #     values['pcb_surface'] = kwargs.get('surface_value')

            file_dict = {
                'gerber_file_id': file_names.get('gerber_file_id'),
                'gerber_atta_id': file_names.get('gerber_atta_id'),
                'gerber_file_name': file_names.get('gerber_file_name'),

                'bom_file_id': file_names.get('bom_file_id'),
                'bom_atta_id': file_names.get('bom_atta_id'),
                'bom_file_name': file_names.get('bom_file_name'),

                'smt_file_id': file_names.get('smt_file_id'),
                'smt_atta_id': file_names.get('smt_atta_id'),
                'smt_file_name': file_names.get('smt_file_name'),
            }
            order_id = request.env['sale.quotation'].sudo().CreateOrUpdatePCBQuote(x_id, values, package=package, unquote=True)
            # # 关联文件
            request.env['sale.order'].sudo().cpo_update_file({'order_id': order_id, 'create_upload_file': file_dict})
        except Exception, e:
            kw.update({
                'error': 'Creation failed, please check the data!',
            })
            _logger.error("(ERROR !!!!) Special order creation: %s (ERROR !!!!)" % e)
            return kw
        kw.update({
            'url': '/my/home',
            'success': 'Created successfully, jumping back to the personal center !',
        })
        return kw


class ContactusMessage(http.Controller):
    """
    联系我们的
    """
    @http.route('/contactus/message', auth='public', type='json', website=True)
    def contactus_message(self, **kw):
        values = {}
        cu_data = kw.get('cu_data')
        if not cu_data.get('name'):
            kw['error'] = 'Name cannot be empty!'
            return kw
        if not cu_data.get('email'):
            kw['error'] = 'E-mail can not be empty!'
            return kw
        if not cu_data.get('phone'):
            kw['error'] = 'Phone cannot be empty!'
            return kw
        if not cu_data.get('company'):
            kw['error'] = 'The company cannot be empty!'
            return kw
        if not cu_data.get('cu_content'):
            kw['error'] = 'The content can not be blank!'
            return kw
        values.update({
            'name': cu_data.get('name'),
            'email': cu_data.get('email'),
            'phone': cu_data.get('phone'),
            'company': cu_data.get('company'),
            'content': cu_data.get('cu_content'),
            'support_type': cu_data.get('support_type'),
            'date': datetime.datetime.now(),
        })
        cu_create = self._contactus_message_create(values)
        if not cu_create:
            kw['error'] = 'Submission failed, please try again later!'
            return kw
        kw['success'] = 'Submit successfully, the staff will contact you email later!'
        kw['url'] = '/page/contactus'
        return kw

    def _contactus_message_create(self, vals):
        """
        关于我们的消息创建
        :param vals:
        :return:
        """
        return False





# class InheritWebsiteSalePCB(cpo_electron_WebsiteSale):

    # @http.route()
    # def old_pcb(self, page=0, category=None, search='', ppg=False, source=None, type=None, ufile=None, **post):
    #     try:
    #         CpoQuotationRecordCode().get_website_source()
    #     except Exception, e:
    #         _logger.error("Error message: %s (empty or not writable)" % e)
    #     return super(InheritWebsiteSalePCB, self).old_pcb(page=0, category=None, search='', ppg=False, source=None, type=None, ufile=None, **post)
    #

