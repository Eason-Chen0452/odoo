# -*- coding: utf-8 -*-
from odoo import http,fields
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
import logging

_logger = logging.getLogger(__name__)

class WebsiteCpoAdvertising(WebsiteForm):
    @http.route('/advertising', auth='public')
    def index(self, **kw):
        return "Hello, world"

    #打折广告
    @http.route('/advertising/billboard/', type='json', auth='public', website=True)
    def list(self, **kw):
        datetime_now_utc = fields.Datetime.to_string(fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz':'utc'}),fields.Datetime.from_string(fields.Datetime.now())))
        rows = http.request.env['cpo_advertising'].sudo().search([('ad_start_time','<=',datetime_now_utc),('ad_end_time','>=',datetime_now_utc)], limit=1)
        return {'ad_content': request.env['ir.ui.view'].render_template('website_cpo_advertising.listing',{
            'objects': rows,
        })}


    #下单页面打折
    @http.route('/advertising/order/page/', type='json', auth='public', website=True)
    def order_list(self, **kw):
        datetime_now_utc = fields.Datetime.to_string(fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz':'utc'}),fields.Datetime.from_string(fields.Datetime.now())))
        rows = http.request.env['cpo_page_advertising'].sudo().search([], limit=1)
        return {'order_page_ad_content': request.env['ir.ui.view'].render_template('website_cpo_advertising.order_page_ad_content',{
            'objects': rows,
        })}

    #通知
    @http.route('/page/natification', type='json', auth='public', website=True)
    def page_natification(self, **kw):
        """
        网站消息通知，展示最新的一条通知
        :param kw:
        :return:
        """
        try:
            re_url = request.httprequest.environ.get('HTTP_REFERER')
            cant_natifi = ['/natification', '/my', '/product', '/pcb', '/pcba', '/contactus', '/cart']
            for n in cant_natifi:
                if n in re_url:
                    content_show = False
                    break
                else:
                    content_show = True
            datetime_now_utc = fields.Datetime.to_string(fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz':'utc'}),fields.Datetime.from_string(fields.Datetime.now())))
            all_na = http.request.env['cpo_notification'].sudo().search([])
            # 判断是否过期
            for all in all_na:
                if all.notice_end_time <= datetime_now_utc:
                    all.state = 'invalid'
            # 取出未过期，且发布的消息
            rows = http.request.env['cpo_notification'].sudo().search([
                ('notice_end_time', '>=', datetime_now_utc),
                ('state', 'in', ['release']),
            ])
            # print rows
            if rows:
                return {'page_natification_temp': request.env['ir.ui.view'].render_template('website_cpo_advertising.page_natification_temp',{
                    'objects': rows[0],
                    'qty': len(rows),
                    'content_show': content_show,
                })}
            else:
                return {}
        except Exception, e:
            _logger.error("Index notice: %s value has been dropped (notice)" % e)
            return {}

    # 所有通知
    @http.route('/natification', type='http', auth='public', website=True)
    def all_natification(self, **kw):
        """
        展示所有的通知
        :param kw:
        :return:
        """
        try:
            values = {}
            datetime_now_utc = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(http.request.env.user.with_context({'tz': 'utc'}),
                                                  fields.Datetime.from_string(fields.Datetime.now())))
            all_na = http.request.env['cpo_notification'].sudo().search([])
            # 判断是否过期
            for all in all_na:
                if all.notice_end_time <= datetime_now_utc:
                    all.state = 'invalid'
            # 取出未过期，且发布的消息
            rows = http.request.env['cpo_notification'].sudo().search([
                ('notice_end_time', '>=', datetime_now_utc),
                ('state', 'in', ['release']),
            ])
            if rows:
                values.update({
                    'values': rows,
                    'content_show': False,
                })
            return request.render("website_cpo_advertising.cpo_all_natification", values)
        except Exception, e:
            _logger.error("Index notice: %s value has been dropped (notice)" % e)
            values.update({
                'values': None,
                'content_show': False,
            })
            request.render("website_cpo_advertising.cpo_all_natification", values)