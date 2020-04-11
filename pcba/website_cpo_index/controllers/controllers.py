# -*- coding: utf-8 -*-
from odoo import http,fields
from odoo import http, _
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_payment.controllers.main import WebsitePayment
from cpo_quotation_record_code import CpoQuotationRecordCode as user_api
import base64
import StringIO
import datetime
import re


class WebsiteCpoAdvertising(WebsiteForm):

    @http.route('/company/video', type='json', auth='public', website=True)
    def cpo_video(self, **kw):
        """
        创建视频链接
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_video'].sudo().search([('cpo_video_title', '=', 'company')], limit=1)

        return rows.cpo_video_link

    @http.route('/process/video', type='json', auth='public', website=True)
    def load_cpo_video(self, **kw):
        """
        加载下单教程视频
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_video'].sudo().search([('cpo_video_title', '=', 'process')], limit=1)

        return rows.cpo_video_link

    #国家列表信息
    @http.route('/cpo_country_list', type='json', auth='public', website=True)
    def pcb_country_list(self, **kw):
        code_country_list = ['US', 'DE', 'GB', 'IL', 'CA', 'FR']
        code_not_country_list = ['TW', 'HK', 'MO', 'US', 'DE', 'GB', 'IL', 'CA', 'FR']
        rows_used = http.request.env['res.country'].sudo().search([('code', 'in', code_country_list)])
        rows = http.request.env['res.country'].sudo().search([('code', 'not in', code_not_country_list)])
        return {'cpo_country_list_temp': request.env['ir.ui.view'].render_template('website_cpo_index.cpo_country_list_temp',{
            'rows_used': rows_used,
            'objects': rows,
        })}

    # 新闻栏目
    @http.route([
        '/news/<model("cpo_news_list"):newlist>',
        '/news/<model("cpo_news_list"):newlist>/page/<int:page>',
    ], type='http', auth='public', website=True)
    def cpoNews(self, page=0, **kw):
        new_list_id = kw['newlist'].id
        new_list = request.env['cpo_news_list'].sudo().search([('id', '=', new_list_id)])
        values = {
            'title': new_list.cpo_new_title,
            'date': new_list.cpo_new_date,
            'editor': new_list.cpo_new_editor,
            'content': new_list.cpo_new_content,
        }
        return http.request.render("website_cpo_index.cpo_new_list_content", {'values': values, 'new_list': new_list})

    # 产品介绍
    @http.route('/product/description', type='json', auth='public', website=True)
    def cpo_product_description(self, **kw):
        """
        产品介绍，描述
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_product_description'].sudo().search([])
        if rows:
            return {'cpo_product_description': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_product_description', {
                    'objects': rows,
                })}
        else:
            return None

    # 图片和标题
    @http.route('/product/img', type='json', auth='public', website=True)
    def cpo_product_img(self, **kw):
        """
        产品介绍，描述
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_product_description'].sudo().search([])
        if rows:
            return {'cpo_product_img_title': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_product_img_title', {
                    'objects': rows,
                })}
        else:
            return None

    # 打包价
    @http.route('/package/price', type='json', auth='public', website=True)
    def cpo_package_price(self, **kw):
        """
        设置打包价返回前端展示
        (包含PCB和PCBA)
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_package_price'].sudo().search([('state', '=', 'release')])
        if rows:
            return {'cpo_get_package_price_list': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_get_package_price_list', {
                    'objects': rows,
                })}
        else:
            return None


    # PCBA 打包价 条件设置
    @http.route('/pcba-condition', type='json', auth='public', website=True)
    def pcba_condition(self, **kw):
        """
        设置PCBA打包价条件，展示在 url：/pcba 的页面，方便后台更新
        当前条件含物料
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_pcba_condition'].sudo().search([('state', '=', 'release')], limit=3)
        if rows:
            return {'pcba_condition': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_pcba_condition_template', {
                    'objects': rows,
                })}
        else:
            return None
    # PCBA 打包价 条件设置
    @http.route('/pcba-material-condition', type='json', auth='public', website=True)
    def pcba_material_condition(self, **kw):
        """
        设置PCBA打包价条件，展示在 url：/pcba 的页面，方便后台更新
        当前条件含物料
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_pcba_condition'].sudo().search([('state', '=', 'release'), ('condition_type', '=', 'yes')], limit=1)
        if rows:
            return {'cpo_pcba_condition_temp': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_pcba_condition_temp', {
                    'objects': rows,
                })}
        else:
            return None

    # PCBA 打包价 条件设置
    @http.route('/pcba-standard-condition', type='json', auth='public', website=True)
    def pcba_standard_condition(self, **kw):
        """
        设置PCBA打包价条件，展示在 url：/pcba 的页面，方便后台更新
        当前条件含物料
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_pcba_condition'].sudo().search([('state', '=', 'release'), ('condition_type', '=', 'standard')], limit=1)
        if rows:
            return {'cpo_pcba_condition_temp': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_pcba_condition_temp', {
                    'objects': rows,
                })}
        else:
            return None

    # PCBA 打包价 条件设置
    @http.route('/pcba-no-material-condition', type='json', auth='public', website=True)
    def pcba_no_material_condition(self, **kw):
        """
        设置PCBA打包价条件
        展示在 url：/pcba 的页面，方便后台更新
        当前物料不含物料
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_pcba_condition'].sudo().search([('state', '=', 'release'), ('condition_type', '=', 'no')], limit=1)
        if rows:
            return {'cpo_pcba_condition_temp': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_pcba_condition_temp', {
                    'objects': rows,
                })}
        else:
            return None

    # 工艺介绍
    @http.route('/advertage/products', type='json', auth='public', website=True)
    def cpo_advertage_product(self, **kw):
        """
        设置工艺介绍返回前端展示
        前端4大项（HDI，Rigid-flex，Multilayer，High Frequency）
        :param kw:
        :return:
        """
        rows = http.request.env['cpo_advertage_products'].sudo().search([])
        if rows:
            return {'cpo_advertage_products_temp': request.env['ir.ui.view'].render_template(
                'website_cpo_index.cpo_advertage_products_temp', {
                    'objects': rows,
                })}
        else:
            return None

    # Banner
    @http.route('/banner/record', type='json', auth='public', website=True)
    def cpo_banner_image(self, **kw):
        """
        设置首页banner返回前端展示
        :param kw:
        :return:
        """
        try:
            values = {}
            rows = http.request.env['cpo_banner_image'].sudo().search([])
            if rows:
                for row in rows:
                    if row.cpo_image_type == 'svg':
                        if row.cpo_banner_img:
                            de_img_data = base64.b64decode(row.cpo_banner_img)
                    else:
                        de_img_data = row.cpo_banner_img

                    values.update({
                        row.id: {
                            'type': row.cpo_image_type,
                            'title': row.cpo_banner_title,
                            'color': row.cpo_main_color,
                            'description': row.cpo_banner_description,
                            'data': de_img_data
                        }
                    })
                return {'cpo_banner_image_temp': request.env['ir.ui.view'].render_template(
                    'website_cpo_index.cpo_banner_image_temp', {
                        'rows': rows
                    })}
            else:
                return False
        except Exception, e:
            return False

    # Material 展示时间段内赠送物料
    # @http.route('/show/material', type='json', auth='public', website=True)
    # def cpo_get_material(self, **kw):
    #     """
    #     展示时间段内赠送物料
    #     :param kw:
    #     :return:
    #     """
    #     try:
    #         material_data = request.env['material.gift'].sudo()
    #         get_material = material_data.get_home_show()
    #         if get_material:
    #             return {'cpo_get_material_temp': request.env['ir.ui.view'].render_template(
    #                 'website_cpo_index.cpo_get_material_temp', {
    #                     'objects': get_material,
    #                 })}
    #         else:
    #             return kw
    #     except Exception, e:
    #         return False

    # Material 所有的电子物料
    @http.route('/page/material', type='http', auth='public', website=True)
    def cpo_page_material_show(self, **kw):
        """
        1、所有电子物料的展示
        :param kw:
        :return:
        """
        values = {}
        try:
            material_data = request.env['material.gift'].sudo()
            show_all_material = material_data.get_independent_show()
            values.update({
                'all_data': show_all_material
            })
            return request.render('website_cpo_index.cpo_all_material_show', values)
        except Exception, e:
            return request.render('website_cpo_index.cpo_all_material_show_404', values)



    # 表面处理数据选项
    @http.route('/select/surface', type='json', auth='public', website=True)
    def cpo_select_surface(self, **kw):
        """
        表面处理的数据组合
        :param kw:
        :return:
        """
        try:
            immersion_gold_list = ['Immersion gold (2 u″)', 'Immersion gold (3 u″)']
            immersion_gold = 'Immersion gold'
            cpo_dict = []
            cpo_click_value = kw.get('cpo_click_value')
            if immersion_gold in cpo_click_value:
                cpo_click_value = 'Immersion gold'
            if kw.get('cpo_type'):
                data_alone = request.env['cpo_click_select_detailed'].sudo().search([
                    ('name', '=', cpo_click_value),
                ])
                for cpo_alone_one in data_alone:
                    data_more = request.env['cpo_click_select_detailed'].sudo().search(
                        [('cpo_detailed_rel', '=', cpo_alone_one.cpo_detailed_rel.name)])
                    for data_a in data_more:
                        if data_a.name not in cpo_dict and data_a.name != cpo_click_value:
                            if data_a.name == 'Immersion gold':
                                for ig_ls in immersion_gold_list:
                                    cpo_dict.append(ig_ls)
                            else:
                                cpo_dict.append(data_a.name)

            kw['val_list'] = cpo_dict
            return kw
        except Exception, e:
            return False

    # 优惠券展示
    @http.route('/cpo/index-coupon', type='http', auth='public', website=True)
    def cpo_index_coupon(self, **kw):
        """
        首页优惠券展示
        :param kw:
        :return:
        """
        try:
            values = {}
            preferential = http.request.env['preferential.cpo_time_and_money'].sudo()
            preferential.checking_function()
            coupon_list = []
            user_id = request.env.user.partner_id.id
            rows = http.request.env['preferential.cpo_time_and_money'].sudo().search([('state', 'not in', ('cancel', 'invalid_over')),
                                                                                      ('cpo_display', '=', True),
                                                                                      ('cpo_full', '=', False),
                                                                                      ('cpo_amount_bool', '=', True)])
            if rows:
                if user_id:
                    for row in rows:
                        customer_user = http.request.env['preferential.cpo_customer_contact'].sudo()
                        customer_db = customer_user.search([('time_money_id', '=', row.id), ('partner_id', '=', user_id)])
                        if customer_db:
                            list_customer = row.id
                            coupon_list.append(list_customer)

                # return {'cpo_index_coupon': request.env['ir.ui.view'].render_template('website_cpo_index.cpo_index_coupon', {
                #     'objects': rows,
                #     'coupon_list': coupon_list,
                # })}
                values.update({
                    'objects': rows,
                    'coupon_list': coupon_list,
                })
                return request.render("website_cpo_index.cpo_index_coupon", values)

            else:
                return False
        except Exception, e:
            return False

    # 现金券展示
    # @http.route('/cpo/index-cash', type='json', auth='public', website=True)
    def cpo_index_cash_coupon(self, **kw):
        """
        首页（现金券）
        :param kw:
        :return:
        """
        try:
            cash_preferential = http.request.env['cash.coupons'].sudo()
            rows = cash_preferential.get_cash_coupon({})
            coupon_list = []
            user_id = request.env.user.partner_id.id
            # rows = http.request.env['preferential.cpo_time_and_money'].sudo().search([('state', 'not in', ('cancel', 'invalid_over')),
            #                                                                           ('cpo_display', '=', True),
            #                                                                           ('cpo_full', '=', False),
            #                                                                           ('cpo_amount_bool', '=', True)])
            # if user_id:
            #     for row in cash_preferential:
            #         customer_user = http.request.env['preferential.cpo_customer_contact'].sudo()
            #         customer_db = customer_user.search([('time_money_id', '=', row.id), ('partner_id', '=', user_id)])
            #         if customer_db:
            #             list_customer = [customer_db.id, user_id, row.id]
            #             coupon_list.append(list_customer)

            return {'index_cash_coupon': request.env['ir.ui.view'].render_template('website_cpo_index.cpo_index_cash_temp', {
                'objects': rows
            })}
        except Exception, e:
            return False

    # 优惠券展示
    # @http.route('/cpo_coupon_list', type='json', auth='public', website=True)
    def order_coupon_list(self, **kw):
        preferential = http.request.env['preferential.cpo_time_and_money'].sudo()
        preferential.checking_function()
        coupon_list = []
        user_id = request.env.user.partner_id.id
        rows = http.request.env['preferential.cpo_time_and_money'].sudo().search([('state', 'not in', ('cancel', 'invalid_over')),
                                                                                  ('cpo_display', '=', True),
                                                                                  ('cpo_full', '=', False),
                                                                                  ('cpo_amount_bool', '=', True)])
        if user_id:
            for row in rows:
                customer_user = http.request.env['preferential.cpo_customer_contact'].sudo()
                customer_db = customer_user.search([('time_money_id', '=', row.id), ('partner_id', '=', user_id)])
                if customer_db:
                    list_customer = [customer_db.id, user_id, row.id]
                    coupon_list.append(list_customer)
        return {'cpo_coupon_list': request.env['ir.ui.view'].render_template('website_cpo_index.cpo_coupon_list', {
            'objects': rows,
            'coupon_list': coupon_list,
        })}

    # 点击领取优惠券
    @http.route('/confrim_coupon', type='json', auth='public', website=True)
    def confrim_coupon(self, **kw):
        """
        优惠券领取！
        :param kw:
        :return:
        """
        values = {}
        user_name = request.env.user.name
        if user_name == 'Public user':
            tips = {
                'tips': 'Please log in first !',
                'url': '/web/login',
            }
            return tips
        else:
            user_id = request.env.user.partner_id.id
            if 'coupon_id' in kw.keys():
                coupon_id = kw['coupon_id']
            else:
                coupon_id = None
            values.update({
                'user_id': user_id,
                'coupon_id': coupon_id
            })
            cpo_coupon = http.request.env['preferential.cpo_time_and_money']
            cpo_received = cpo_coupon.get_preferential_settings(values)

            return cpo_received

    # 所有优惠券展示
    @http.route('/coupon', type='http', auth='public', website=True)
    def coupon(self, **kw):

        preferential = http.request.env['preferential.cpo_time_and_money']
        preferential.checking_function()
        coupon_list = []
        user_id = request.env.user.partner_id.id
        rows = http.request.env['preferential.cpo_time_and_money'].sudo().search([('state', 'not in', ('cancel', 'invalid_over')),
                                                                                  ('cpo_display', '=', True),
                                                                                  ('cpo_full', '=', False),
                                                                                  ('cpo_amount_bool', '=', True)])
        if user_id:
            for row in rows:
                customer_user = http.request.env['preferential.cpo_customer_contact'].sudo()
                customer_db = customer_user.search([('time_money_id', '=', row.id), ('partner_id', '=', user_id)])
                if customer_db:
                    list_customer = row.id
                    coupon_list.append(list_customer)

        values = {
            'objects': rows,
            'coupon_list': coupon_list,
        }
        return request.render("website_cpo_index.cpo_coupon_center", values)

    # 上传文件
    @http.route('/upload/file/json', type='json', auth='public', website=True)
    def upload_file_all(self, **kw):
        """
        前端文件上传
        :param kw:
        :return:
        """
        try:
            atta_pool = request.env['ir.attachment'].sudo()
            res_atta_pool = request.env['cpo_annex_file'].sudo()
            datas = kw.get('datas')
            # datas = base64.b64encode(datas)
            size_length = 30 * 1024 * 1024
            if datas and len(base64.b64decode(datas)) > size_length:
                return {'error': 'file size length must less than 30M.'}
            if not datas:
                return {'error': 'file format error.'}
            tag_name = kw.get('tag_name')
            if tag_name == 'gerber_file':
                file_type = 'Gerber File'
            elif tag_name == 'bom_file':
                file_type = 'BOM File'
            else:
                file_type = 'SMT File'
            # datas = base64.b64decode(datas)
            name = kw.get('name')
            if request.env.user.name:
                user_name = request.env.user.name
            user_info = user_api().cpo_get_user_data()
            file_vals = {
                'name': name,
                'file_type': file_type,
                'order_type': kw.get('order_type'),
                'datas': datas,
                'upload_date': datetime.datetime.now(),
                'user_name': user_name,
                'user_ip': user_info.get('user_ip'),
                'session_id': user_info.get('session_id'),
                'cpo_city': user_info.get('cpo_city'),
                'cpo_country': user_info.get('cpo_country'),
            }

            atta_file = res_atta_pool.create(file_vals)

            vals = {
                'name': name,
                'description': file_type,
                'res_model': 'cpo_annex_file',
                'type': 'binary',
                'public': True,
                'datas': datas,
                'res_id': atta_file.id,
                'datas_fname': name,
            }

            atta_id = atta_pool.create(vals)
            kw['atta_id'] = atta_id.id
            kw['file_id'] = atta_file.id
            kw['file_name'] = name
            return kw
        except Exception, e:
            kw['error'] = 'Upload failed !'
            return kw

    # 购物车下载附件
    @http.route('/down/file', type='http', auth='public', csrf=False)
    def cpo_download_attachment(self, attaId=None, **kwargs):
        """
        在购物车订单中下载附件
        :param kwargs: attachment_id
        :return:
        """
        if attaId:
            rand_str = attaId[5:]
            str_decrypt = base64.b64decode(rand_str).decode()  # 字符串解密
            aId = int(str_decrypt)
            attachment_id = aId
        else:
            attachment_id = kwargs.get('attachment_id')
        #获取附件对象，以数组返回
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"]
        )
        #在返回的数组中获取对象，如果存在url则重新定向
        if attachment:
            attachment = attachment[0]
        else:
            return request.redirect('/down/file')
        res_id = attachment['res_id']
        if attachment["type"] == "url":
            if attachment["url"]:
                return request.redirect(attachment["url"]) #直接从URL下载
            else:
                return request.not_found()
        elif attachment["datas"]:
            # data = StringIO(base64.standard_b64decode(attachment["datas"]))
            #解码返回下载链接
            data = StringIO.StringIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()

    @http.route('/get_invoices', type='json', auth='public', website=True)
    def get_invoices(self, **kw):
        """
        用途：用户选择使用发票（订单支付）
        状态：当前作废（待使用）
        个人中心发票
        :param kw:
        :return:
        """
        try:
            invoices = http.request.env['account.invoice'].sudo()
            get_invoices_data = invoices.get_website_account_inv(kw)
            kw['total_amount'] = get_invoices_data.get('Amount Total')
            kw['currency'] = get_invoices_data.get('Symbol')
            kw['invoices'] = get_invoices_data.get('number_dict')
        except Exception, e:
            kw['error'] = e
        return kw

    @http.route('/add_google_analytics', type='json', auth='public', website=True)
    def add_google_analytics(self, **post):

        cpo_google_pool = http.request.env['cpo_google_analytics'].sudo()
        cpo_browse_link = post.get('cpo_browse_link')
        cpo_browse_time = str(post.get('cpo_browse_time'))+' ms'
        cpo_ip = post.get('cpo_ip')
        cpo_google_pool.add_google_analytics(cpo_browse_link, cpo_browse_time, cpo_ip)

        return post

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

    def comfile_data(self, vals):
        """
        解析PCBA和PCB数据，取各自的重要数据
        :param vals:
        :return:
        """

        order_type = vals.get('order_name')
        if order_type == 'PCBA':
            result_data = self.pcba_data_analysis(vals)
        elif order_type == 'PCBA Package Price':
            result_data = self.pcba_package_data_analysis(vals)
        else:
            result_data = self.pcb_data_analysis(vals)

        return result_data

    def pcba_package_data_analysis(self, args):
        """
        PCBA 打包价数据提取
        :param args:
        :return:
        """
        vals = args.get('data')
        order_type = args.get('order_name')
        file_data = args.get('file_data')
        file_name = self.file_check_record(file_data)
        pcba_package_value = vals.get('package_form')

        record_data = {
            'order_type': order_type,
            'quantity': int(pcba_package_value.get('pcba_package_qty') or 0),
            'width': float(pcba_package_value.get('pcba_package_width') or 0),
            'lenght': float(pcba_package_value.get('pcba_package_length') or 0),
            'thickne': float(pcba_package_value.get('pcba_package_thick') or 0),
            'file_name': str(file_name),
            'total': vals.get('pcba_package').get('Total Price'),
            'cpo_time': datetime.datetime.now(),
            'bom_type': str(pcba_package_value.get('pcba_material_type') or ''),
            'smt_qty': int(pcba_package_value.get('pcba_package_smt') or 0),
            'dip_qty': int(pcba_package_value.get('pcba_package_dip') or 0),
            'smt_side': pcba_package_value.get('pcba_package_smt_side')
        }
        return record_data

    def pcba_data_analysis(self, args):
        """
        PCBA数据分析提取，将需要的数据提取存储记录
        :param args:
        :return:
        """
        vals = args.get('data')
        order_type = args.get('order_name')
        file_data = args.get('file_data')
        file_name = self.file_check_record(file_data)
        pcba_value = vals.get('pcba_value')
        record_data = {
            'order_type': order_type,
            'quantity': int(pcba_value.get('cpo_quantity') or 0),
            'width': float(pcba_value.get('cpo_width') or 0),
            'lenght': float(pcba_value.get('cpo_length') or 0),
            'thickne': float(pcba_value.get('pcb_thickness') or 0),
            'file_name': str(file_name),
            'total': vals.get('cpo_price_list').get('ele_tatol'),
            'cpo_time': datetime.datetime.now(),
            'bom_type': '',
            'smt_qty': int(pcba_value.get('cpo_smt_qty') or 0),
            'dip_qty': int(pcba_value.get('cpo_dip_qty') or 0),
            'smt_side': pcba_value.get('cpo_side')
        }
        return record_data

    def pcb_data_analysis(self, args):
        """
        解析PCB订单记录的数据
        :param args:
        :return:
        """
        pcb_special = None
        vals = args.get('data')
        order_type = args.get('order_name')
        if order_type == 'HDI':
            order_total = vals.get('hdi_quotation').get('value').get('Total Cost')
        elif order_type == 'Rigid-FLex':
            order_total = vals.get('value').get('value').get('Total Cost')
        elif order_type == 'PCB Package':
            order_total = vals.get('pcb_package').get('value').get('Total Cost')
        else:
            order_total = vals.get('Total Cost')
        file_data = args.get('file_data')
        file_name = self.file_check_record(file_data)
        pcb_value = vals.get('pcb_value')
        surface_data = pcb_value.get('pcb_surfaces')
        if surface_data and surface_data.get('pcb_surface'):
            surface = surface_data.get('pcb_surface')
            golden_finger_thickness = 0
        else:
            surface = surface_data.get('surface_value')
            golden_finger_thickness = surface_data.get('gold_finger_thickness')
        # if pcb_value.get('pcb_surfaces').get('pcb_surface'):
        #     surface = pcb_value.get('pcb_surfaces').get('pcb_surface')
        # else:
        #     surface = pcb_value.get('pcb_surfaces').get('surface_value')
        if args.get('data').get('pcb_soft_hard'):
            flex_number = args.get('data').get('pcb_soft_hard').get('cpo_flex_number')
        else:
            flex_number = None
        pcb_special = pcb_value.get('pcb_special_requirements')
        if pcb_special:
            pcb_special = pcb_special
        record_data = {
            'order_type': order_type,
            'quantity': int(pcb_value.get('cpo_quantity') or 0),
            'width': float(pcb_value.get('pcb_breadth') or 0),
            'lenght': float(pcb_value.get('pcb_length') or 0),
            'thickne': float(pcb_value.get('pcb_thickness') or 0),
            'file_name': str(file_name),
            'cpo_time': datetime.datetime.now(),
            'total': order_total,
            'panel_size': pcb_value.get('pcb_pcs_size'),
            'item_qty': pcb_value.get('pcb_item_size'),
            'material': pcb_value.get('pcb_type'),
            'inner_copper': float(pcb_value.get('pcb_inner_copper') or 0),
            'outer_copper': float(pcb_value.get('pcb_outer_copper') or 0),
            'layers': pcb_value.get('pcb_layer'),
            'mask_color': pcb_value.get('pcb_solder_mask'),
            'silkscreen_color': pcb_value.get('pcb_silkscreen_color'),
            'surface': surface,
            'e_test': pcb_value.get('pcb_test'),
            'flex_number': flex_number,
            'golden_finger_thickness': golden_finger_thickness,
            'Semi_hole': pcb_special.get('Semi_hole'),
            'Edge_plating': pcb_special.get('Edge_plating'),
            'Impedance': pcb_special.get('Impedance'),
            'Press_fit': pcb_special.get('Press_fit'),
            'Peelable_mask': pcb_special.get('Peelable_mask'),
            'Carbon_oil': pcb_special.get('Carbon_oil'),
            'Min_line_width': pcb_special.get('Min_line_width'),
            'Min_line_space': pcb_special.get('Min_line_space'),
            'Min_aperture': pcb_special.get('Min_aperture'),
            'Total_holes': pcb_special.get('Total_holes'),
            'Copper_weight_wall': pcb_special.get('Copper_weight_wall'),
            'Number_core': pcb_special.get('Number_core'),
            'PP_number': pcb_special.get('PP_number'),
            'Total_test_points': pcb_special.get('Total_test_points'),
            'Blind_and_buried_hole': pcb_special.get('Blind_and_buried_hole'),
            'Blind_hole_structure': pcb_special.get('Blind_hole_structure'),
            'Depth_control_routing': pcb_special.get('Depth_control_routing'),
            'Number_back_drilling': pcb_special.get('Number_back_drilling'),
            'Countersunk_deep_holes': pcb_special.get('Countersunk_deep_holes'),
            'Laser_drilling': pcb_special.get('Laser_drilling'),
            'Inner_hole_line': pcb_special.get('Inner_hole_line'),
            'The_space_for_drop_V_cut': pcb_special.get('The_space_for_drop_V_cut'),
        }
        return record_data

    def file_check_record(self, file_data):
        """
        获取文件名
        :param file_data:
        :return:
        """
        file_type = ''
        file_all = [file_data.get('gerber_file_id'), file_data.get('bom_file_id'), file_data.get('smt_file_id')]
        file_ids = [f for f in file_all if f]
        if file_ids:
            att_id = request.env['cpo_annex_file'].sudo().search([('id', 'in', file_ids)])
            for f in att_id:
                file_type = str(file_type) + str(f.file_type) + ' ; '
        else:
            file_type = 'No File'
        return file_type

    def cpo_handle_file(self, file_data, record_id, session_data):
        """
        关联文件
        :param file_data:
        :param record_id:
        :return:
        """
        if file_data:
            request.env['cpo_annex_file'].sudo().cpo_sync_att_to_quotation_record(file_data, record_id, session_data)
            return True
        else:
            return False

    def get_user_data(self):
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
                user_country_name = get_ip_info.get('country_name')
                user_city_name = get_ip_info.get('city').encode('utf-8')
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

    @http.route('/set_quotation_reacord', type='json', auth='public', website=True)
    def set_quotation_reacord(self, **kw):
        """
        网页报价记录
        :param kw:
        :return:
        """
        try:
            cpo_s_u = self.cpo_get_user_info()
            partner_info = request.env['cpo_session_association'].sudo().check_session_info(cpo_s_u)
            partner_user = {'partner_info': partner_info.get('get_data')}
            user_info = {
                # 'user_id': request.env.user.id,
                # 'user_name': request.env.user.name,
                'user_name': partner_info.get('get_customer'),
            }
            # record_model = request.env['cpo_quotation_record'].sudo()
            file_data = kw.get('file_data')
            session_data = self.get_user_data()
            get_com_data = self.comfile_data(kw)
            record_data = dict(get_com_data.items() + session_data.items() + user_info.items()+partner_user.items())
            check_re = self.comparison_time(record_data)
            if check_re:
                self.cpo_handle_file(file_data, check_re, session_data)
                self.cpoSetFileId(file_data, check_re)
                return check_re.id
            else:
                return False
            # self.cpo_handle_file(file_data, record_id)
        except Exception, e:
            return False

    def cpoSetFileId(self, files, check_re):
        fls = []
        if files.get('gerber_atta_id'):
            fls.append(int(files.get('gerber_atta_id')))
        if files.get('bom_atta_id'):
            fls.append(int(files.get('bom_atta_id')))
        if files.get('smt_atta_id'):
            fls.append(int(files.get('smt_atta_id')))
        if check_re:
            check_re.update({
                'file_ids': [(6, 0, fls)],
            })
        return True

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

    def comparison_time(self, vals):
        """
        去除重复数据，重复数据不保存
        :param vals:
        :return:
        """
        try:
            hours = self.cpo_record_time_setting()
            order_list = ['HDI', 'Rigid-FLex', 'PCB Package', 'PCB']
            format_pattern = "%Y-%m-%d %H:%M:%S"
            datetime_now_utc = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz': 'utc'}),
                                                  fields.Datetime.from_string(fields.Datetime.now())))
            get_time = datetime.datetime.strptime(datetime_now_utc, format_pattern) - datetime.timedelta(hours=hours)
            comparison_time = get_time.strftime(format_pattern)

            time_domain = [
                ('cpo_time', '>', comparison_time)
            ]

            domain_base = [
                ('order_type', '=', vals.get('order_type')),
                ('quantity', '=', int(vals.get('quantity') or 0)),
                ('width', '=', float(vals.get('width') or 0)),
                ('lenght', '=', float(vals.get('lenght') or 0)),
                ('thickne', '=', float(vals.get('thickne') or 0)),
                ('session_id', '=', vals.get('session_id'))
            ]

            intention = [
                ('quantity', '=', int(vals.get('quantity') or 0)),
                ('width', '=', float(vals.get('width') or 0)),
                ('lenght', '=', float(vals.get('lenght') or 0)),
                ('thickne', '=', float(vals.get('thickne') or 0)),
                ('session_id', '=', vals.get('session_id'))
            ]

            pcb_domain = [
                ('panel_size', '=', vals.get('panel_size')),
                ('item_qty', '=', vals.get('item_qty')),
                ('material', '=', vals.get('material')),
                ('inner_copper', '=', vals.get('inner_copper')),
                ('outer_copper', '=', vals.get('outer_copper')),
                ('layers', '=', vals.get('layers')),
                ('mask_color', '=', vals.get('mask_color')),
                ('silkscreen_color', '=', vals.get('silkscreen_color')),
                ('surface', '=', vals.get('surface')),
                ('e_test', '=', vals.get('e_test'))
            ]

            pcba_domain = [
                ('bom_type', '=', vals.get('bom_type')),
                ('smt_qty', '=', int(vals.get('smt_qty') or 0)),
                ('dip_qty', '=', int(vals.get('dip_qty') or 0)),
                ('smt_side', '=', vals.get('smt_side'))
            ]

            intention_list = intention+time_domain

            order_type = vals.get('order_type')
            if order_type in order_list:
                self.pcb_and_pcba_record(domain_base+pcb_domain+time_domain, vals, order_type="PCB")
                pcb_pool = request.env['cpo_pcb_record'].sudo()
                pcba_pool = request.env['cpo_pcba_record'].sudo()
                res_result = self.check_pcb_and_pcba_intention(pcba_pool, intention_list)
                records_obj = pcb_pool.search(domain_base+pcb_domain+time_domain)
                if len(records_obj) >= 1:
                    return False
                else:
                    record_id = pcb_pool.create(vals)
                    if res_result:
                        record_id.cpo_intention = 'yes'
                    return record_id
            else:
                self.pcb_and_pcba_record(domain_base + pcb_domain + pcba_domain + time_domain, vals, order_type="PCBA")
                pcba_pool = request.env['cpo_pcba_record'].sudo()
                pcb_pool = request.env['cpo_pcb_record'].sudo()
                res_result = self.check_pcb_and_pcba_intention(pcb_pool, intention_list)
                records_obj = pcba_pool.search(domain_base + pcba_domain + time_domain)
                if len(records_obj) >= 1:
                    return False
                else:
                    record_id = pcba_pool.create(vals)
                    if res_result:
                        record_id.cpo_intention = 'yes'
                    return record_id
        except Exception, e:
            return False

    def check_pcb_and_pcba_intention(self, obj, vals):
        try:
            res_data = obj.search(vals)
            if len(res_data) > 0:
                for res in res_data:
                    res.cpo_intention = 'yes'
                return True
        except Exception, e:
            return False

    def pcb_and_pcba_record(self, all_domain, values, order_type=None):
        obj_pool = request.env['cpo_pcb_and_pcba_record'].sudo()
        pcb_and_pcba = obj_pool.search(all_domain)
        record_dict = dict(values)
        if len(pcb_and_pcba) <= 0:
            if order_type == 'PCB':
                record_dict.update({
                    'bom_type': 0,
                    'smt_qty': 0,
                    'dip_qty': 0,
                    'smt_side': 0
                })
            else:
                record_dict.update({
                    'panel_size': None,
                    'item_qty': None,
                    'material': None,
                    'inner_copper': '',
                    'outer_copper': '',
                    'layers': None,
                    'mask_color': None,
                    'silkscreen_color': None,
                    'surface': None,
                    'e_test': None
                })
            obj_pool.create(record_dict)
        return True

    @http.route('/get/cookie', type='json', auth='public', website=True)
    def get_cookie_value(self, **kw):
        try:
            rows = request.env['cpo_cookie_duration'].sudo().search([('state', '=', 'release')], limit=1)
            if rows:
                return rows.cookie_time
            else:
                return False
        except Exception, e:
            return False

    @http.route('/service/protocol', type='json', auth='public', website=True)
    def save_service_protocol(self, **kw):
        """
        弹出服务协议，客户点击时记录cookie（记录每24小时弹出1次）
        :param kw:
        :return:
        """
        try:
            cpo_s_u = self.cpo_get_user_info()
            partner_info = request.env['cpo_session_association'].sudo().check_session_info(cpo_s_u)
            # partner_user = {'partner_info': partner_info.id}
            session_data = self.get_user_data()
            # user_info = {
            #     'user_id': request.env.user.id,
            #     'user_name': request.env.user.name,
            # }
            partner_user = {'partner_info': partner_info.get('get_data')}
            user_info = {
                'user_name': partner_info.get('get_customer'),
            }
            content_data = {
                'order_type': 'Service Protocol',
                'quantity': 0,
                'width': 0,
                'lenght': 0,
                'thickne': 0,
                'file_name': None,
                'cpo_time': datetime.datetime.now(),
                'total': 0,
            }
            record_data = dict(content_data.items() + session_data.items() + user_info.items() + partner_user.items())
            self.check_service_protocol(record_data)

        except Exception, e:
            return False

    def check_service_protocol(self, vals):
        format_pattern = "%Y-%m-%d %H:%M:%S"
        datetime_now_utc = fields.Datetime.to_string(
            fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz': 'utc'}),
                                              fields.Datetime.from_string(fields.Datetime.now())))
        get_time = datetime.datetime.strptime(datetime_now_utc, format_pattern) - datetime.timedelta(hours=24)
        comparison_time = get_time.strftime(format_pattern)

        time_domain = [
            ('cpo_time', '>', comparison_time),
            ('session_id', '=', vals.get('session_id'))
        ]
        obj_model = request.env['cpo_service_record'].sudo()
        get_val = obj_model.search(time_domain)

        if len(get_val) < 1:
            obj_model.create(vals)
        return True


    # @http.route('/set_quotation_reacord', type='json', auth='public', website=True)
    # def set_quotation_reacordddddd(self, **kw):
    #     """
    #     用户点击报价，记录相关的数据
    #     :param kw:
    #     :return:
    #     """
    #
    #     try:
    #         data = {}
    #         get_ip_info = self.add_recode_ip_inf(request, data)
    #         session_id = request.httprequest.cookies.get('session_id').encode('utf-8')
    #         if get_ip_info:
    #             user_ip_addr = get_ip_info.get('ip')
    #             if get_ip_info.get('country_name'):
    #                 user_country_name = get_ip_info.get('country_name').encode('utf-8')
    #                 user_city_name = get_ip_info.get('city').encode('utf-8')
    #             else:
    #                 user_country_name = ''
    #                 user_city_name = ''
    #         else:
    #             user_ip_addr = ''
    #             user_country_name = ''
    #             user_city_name = ''
    #
    #         session_data = {
    #             'cpo_country': user_country_name,
    #             'user_ip': user_ip_addr,
    #             'session_id': session_id,
    #             'cpo_city': user_city_name,
    #         }
    #         get_com_data = self.comfile_data(kw)
    #
    #         values = kw.get('record_data')
    #         file_data = values.get('file_name')
    #         record_model = request.env['cpo_quotation_record'].sudo()
    #         atta_pool = request.env['ir.attachment'].sudo()
    #         file_ids = []
    #         file_type = ''
    #         att_id = None
    #         if file_data:
    #             if values.get('order_type') == 'PCBA':
    #                 file_all = [file_data.get('gerber_file_id'), file_data.get('bom_file_id'), file_data.get('smt_file_id')]
    #                 for fa in file_all:
    #                     if fa:
    #                         file_ids.append(fa)
    #                 if file_ids:
    #                     att_id = request.env['cpo_annex_file'].sudo().search([('id', 'in', file_ids)])
    #                     for f in att_id:
    #                         file_type = str(file_type) + str(f.file_type) + ' ; '
    #                 else:
    #                     file_type = 'No File'
    #             elif values.get('order_type') == 'PCBA Package Price':
    #                 file_all = [file_data.get('gerber_file_id'), file_data.get('bom_file_id'),
    #                             file_data.get('smt_file_id')]
    #                 for fa in file_all:
    #                     if fa:
    #                         file_ids.append(fa)
    #                 if file_ids:
    #                     att_id = request.env['cpo_annex_file'].sudo().search([('id', 'in', file_ids)])
    #                     for f in att_id:
    #                         file_type = str(file_type) + str(f.file_type) + ' ; '
    #                 else:
    #                     file_type = 'No File'
    #             else:
    #                 file_id = file_data.get('gerber_file_id')
    #                 if file_id:
    #                     att_id = request.env['cpo_annex_file'].sudo().search([('id', '=', file_id)])
    #                     file_type = att_id.file_type
    #                 else:
    #                     file_type = 'No File'
    #
    #         else:
    #             file_type = 'No File'
    #
    #         record_data = {
    #             'order_type': values.get('order_type'),
    #             'quantity': values.get('quantity'),
    #             'layers': values.get('layers'),
    #             'width': values.get('width'),
    #             'lenght': values.get('lenght'),
    #             'smt_qty': values.get('smt_qty'),
    #             'thickne': values.get('thickne'),
    #             'smt_side': values.get('smt_side'),
    #             'file_name': file_type,
    #             'mask_color': values.get('mask_color'),
    #             'silkscreen_color': values.get('silkscreen_color'),
    #             'cpo_country': user_country_name,
    #             'user_ip': user_ip_addr,
    #             'session_id': session_id,
    #             'cpo_city': user_city_name,
    #             'total': values.get('total'),
    #             'cpo_time': datetime.datetime.now()
    #         }
    #         check_re = self.check_record(record_data)
    #         if check_re:
    #             record_id = record_model.create(record_data)
    #         else:
    #             return False
    #
    #         # 文件处理
    #         handle_file = self.cpo_handle_file(kw.get('file_data'))
    #
    #
    #         if att_id:
    #             if values.get('order_type') == 'PCBA':
    #                 for a_id in att_id:
    #                     vals = {
    #                         'name': a_id.file_type,
    #                         'description': None,
    #                         'res_model': 'cpo_quotation_record',
    #                         'type': 'binary',
    #                         'public': True,
    #                         'datas': a_id.datas,
    #                         'res_id': record_id.id,
    #                         'datas_fname': a_id.file_type,
    #                     }
    #                     atta_pool.create(vals)
    #             else:
    #                 vals = {
    #                     'name': file_data.get('gerber_file_name'),
    #                     'description': None,
    #                     'res_model': 'cpo_quotation_record',
    #                     'type': 'binary',
    #                     'public': True,
    #                     'datas': att_id.datas,
    #                     'res_id': record_id.id,
    #                     'datas_fname': file_data.get('gerber_file_name'),
    #                 }
    #                 atta_pool.create(vals)
    #     except Exception, e:
    #         return False



        # records_obj_gt = request.env['cpo_quotation_record'].sudo().search([
        #     ('session_id', '=', vals.get('session_id')),
        #     ('cpo_time', '>', comparison_time)
        #
        # ])
        # records_obj_lt = request.env['cpo_quotation_record'].sudo().search([
        #     ('session_id', '=', vals.get('session_id')),
        #     ('cpo_time', '>=', comparison_time),
        #     ('cpo_time', '<=', datetime_now_utc)
        # ])
        #
        # get_records = None
        # if len(records_obj_gt) >= 1:
        #     if len(records_obj_lt) < 1:
        #         get_records = self.check_record_date(vals)
        # else:
        #     if len(records_obj_lt) >= 1:
        #         get_records = False
        #     else:
        #         get_records = self.check_record_date(vals)
        # return get_records

    # def check_record_date(self, vals):
    #     records = request.env['cpo_quotation_record'].sudo().search([
    #         ('order_type', '=', vals.get('order_type')),
    #         ('quantity', '=', int(vals.get('quantity') or 0)),
    #         ('width', '=', float(vals.get('width') or 0)),
    #         ('lenght', '=', float(vals.get('lenght') or 0)),
    #         ('smt_qty', '=', int(vals.get('smt_qty') or 0)),
    #         ('thickne', '=', float(vals.get('thickne') or 0)),
    #         ('layers', '=', vals.get('layers')),
    #         ('smt_side', '=', vals.get('smt_side')),
    #         ('mask_color', '=', vals.get('mask_color')),
    #         ('silkscreen_color', '=', vals.get('silkscreen_color'))
    #     ])
    #     if len(records) >= 1:
    #         return False
    #     else:
    #         return True

# 继承website_payment 模块，使用/website_payment/pay 支付
# class WebsitePayment(WebsitePayment):
#
#     @http.route(['/website_payment/pay'], type='http', auth='public', website=True)
#     def pay(self, reference='', amount=False, currency_id=None, acquirer_id=None, **kw):
#         env = request.env
#         user = env.user.sudo()
#
#         currency_id = currency_id and int(currency_id) or user.company_id.currency_id.id
#         currency = env['res.currency'].browse(currency_id)
#
#         # Try default one then fallback on first
#         acquirer_id = acquirer_id and int(acquirer_id) or \
#             env['ir.values'].get_default('payment.transaction', 'acquirer_id', company_id=user.company_id.id) or \
#             env['payment.acquirer'].search([('website_published', '=', True), ('company_id', '=', user.company_id.id)])[0].id
#
#         acquirer = env['payment.acquirer'].with_context(submit_class='btn btn-primary pull-right',
#                                                         submit_txt=_('Pay Now')).browse(acquirer_id)
#         # auto-increment reference with a number suffix if the reference already exists
#         reference = request.env['payment.transaction'].get_next_reference(reference)
#
#         partner_id = user.partner_id.id if user.partner_id.id != request.website.partner_id.id else False
#
#         payment_form = acquirer.sudo().render(reference, float(amount), currency.id, values={'return_url': '/website_payment/confirm', 'partner_id': partner_id})
#         values = {
#             'reference': reference,
#             'acquirer': acquirer,
#             'currency': currency,
#             'amount': float(amount),
#             'payment_form': payment_form,
#         }
#         return request.render('website_payment.pay', values)
