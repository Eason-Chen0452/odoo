# -*- coding: utf-8 -*-

import logging
from urlparse import urlparse
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


# session 表
class SessionAssociation(models.Model):
    _inherit = 'cpo_session_association'

    trial_ids = fields.One2many('cpo_pcb_and_pcba_record', 'partner_info', 'Website Quotation Record')  # 这个session的试价记录
    behavior_ids = fields.One2many('website_cpo_index.cpo_website_source', 'session_id', 'Behavior Record')  # 这个session的行为记录
    session_ip = fields.Char('Session IP')
    session_city = fields.Char('Session City')
    session_country = fields.Char('Session Country')

    # 检查进来的Session 用于 调用 只返回session表的id号
    def CheckSession(self, session_id):
        self._cr.execute("SELECT ID FROM CPO_SESSION_ASSOCIATION WHERE SESSION_ID=%s ORDER BY ID DESC", (session_id, ))
        x_id = self._cr.dictfetchall()
        if x_id:
            x_id = self.browse(x_id[0].get('id'))
        return x_id

    # 创建没有的session
    def CreateSession(self, value):
        value.update({
            'name': hash(value.get('session_id')),
            'cpo_time': fields.Datetime.now(),
        })
        if value.get('user_id') != self.env.ref('base.public_user').id:
            x_dict = self.UpdateAssociatedCustomer(value=value)
            if x_dict:
                value.update(x_dict)
        return self.create(value)

    # 更新 关联用户
    def UpdateAssociatedCustomer(self, value=False, user_id=False, session=False):
        user_id = user_id if user_id else value.get('user_id')
        self._cr.execute('SELECT ID FROM PERSONAL_CENTER WHERE USER_ID=%s', (user_id,))
        x_dict = self._cr.dictfetchall()
        if x_dict:
            x_dict = self.env['personal.center'].browse(x_dict[0].get('id'))
            x_dict = {
                'customer_name': x_dict.id,
                'user_name': x_dict.name,
                'user_id': x_dict.user_id.id,
                'cpo_time': fields.Datetime.now(),
            }
            if value:
                return x_dict
            elif session:
                session.write(x_dict)
        return False

    # 临时作用将session的ip 国家 城市 整理赋值
    def session_ip_city_country(self):
        data = self.search([])
        for x_id in data:
            value = None
            if x_id.trial_ids:
                value = max(x_id.trial_ids)
                x_id.write({'session_ip': value.user_ip})
            elif x_id.behavior_ids:
                value = max(x_id.behavior_ids)
                x_id.write({'session_ip': value.cpo_ip})
            x_id.write({
                'session_city': value.cpo_city,
                'session_country': value.cpo_country,
                'cpo_time': value.cpo_time if value.cpo_time else value.write_date,
            })


# 来源表 大表
class ClientSourceWebsite(models.Model):
    _inherit = 'website_cpo_index.cpo_partner_source'

    # 将进来的网站进行解析 如果没有创建 有返回一个id号
    def ParsingWebsite(self, url):
        url = url if url else 'https://www.icloudfactory.com'
        source_url = urlparse(url).netloc
        self._cr.execute('SELECT ID FROM website_cpo_index_cpo_partner_source WHERE NAME=%s', (source_url, ))
        x_id = self._cr.dictfetchall()
        if x_id:
            return x_id[0].get('id'), url
        x_id = self.create({
            'cpo_name': source_url,
            'name': source_url,
            'cpo_time': fields.Datetime.now()
        })
        return x_id.id, url


# 来源下的子表
class ClientSourceWebsiteLine(models.Model):
    _inherit = 'website_cpo_index.all_partner_source'

    def ParsingWebsiteLine(self, x_id, url, session_id):
        self._cr.execute('SELECT ID FROM website_cpo_index_all_partner_source WHERE site_name=%s and cpo_name=%s and session_id=%s', (x_id, url, session_id))
        source_id = self._cr.dictfetchall()
        if source_id:
            self.browse(source_id[0].get('id')).write({'cpo_time': fields.Datetime.now()})
            return self.browse(source_id[0].get('id'))
        return self.create({
            'site_name': x_id,
            'cpo_time': fields.Datetime.now(),
            'session_id': session_id,
            'cpo_name': url,
        })



# 记录行为表
class ClientWebsiteBehavior(models.Model):
    _inherit = 'website_cpo_index.cpo_website_source'

    def CheckBehavior(self, value):
        session, path, source = value.get('session'), value.get('path'), value.get('source')
        self._cr.execute('SELECT ID FROM website_cpo_index_cpo_website_source WHERE customer_related=%s and session_id=%s and access_path=%s', (source.id, session.id, path))
        x_id = self._cr.dictfetchall()
        if x_id:
            self.browse(x_id[0].get('id')).write({
                'cpo_time': fields.Datetime.now(),
                'cpo_city': session.session_city,
                'cpo_country': session.session_country,
                'cpo_ip': session.session_ip,
                'user_id': session.customer_name.id,
                'user_name': session.user_name,
            })
            return True
        self.create({
            'access_path': path,
            'cpo_city': session.session_city,
            'cpo_country': session.session_country,
            'cpo_ip': session.session_ip,
            # 'customer_related': source.id,
            'cpo_source': source.cpo_name,
            'session_id': session.id,
            'cpo_time': fields.Datetime.now(),
            'user_id': session.customer_name.id,
            # 'user_name': session.user_name,
        })
