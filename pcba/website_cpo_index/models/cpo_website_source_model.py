#-*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import time
import logging
import re
import urlparse

_logger = logging.getLogger(__name__)

SELECT_INTENTION = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

class CpoPartnerSource(models.Model):
    """
    记录网站来源，例如来自百度的推广等。
    """

    _name = "website_cpo_index.cpo_partner_source"
    _order = "id desc"

    @api.model
    def _cpo_set_time(self):
        now_time = datetime.datetime.now()
        return now_time

    cpo_name = fields.Char(string="Site Name")
    cpo_type = fields.One2many('website_cpo_index.cpo_website_source', 'customer_related', string="Website Type")
    source_id = fields.One2many('website_cpo_index.all_partner_source', 'site_name', string="Source ID")
    name = fields.Char(string="Website Address")
    user_number = fields.Integer(string="User Number", default=0, compute="_get_user_number", store=False)
    partner_ids = fields.Many2many('website_cpo_index.website_tag', 'tag_partner_rel', 'tag_id', 'partner_id', string='Tags')
    cpo_time = fields.Datetime(string="Last update time", default=_cpo_set_time)
    # internal_keyword = fields.One2many('routing_parameter.internal_keyword', 'site_name', string="Internal Keyword")
    # external_keyword = fields.One2many('routing_parameter.external_keyword', 'site_name', string="External Keyword")
    # exception_keyword = fields.One2many('routing_parameter.exception_keyword', 'site_name', string="Exception Keyword")

    def search_users_func(self):
        user_list = []
        reg = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)|([a-zA-Z]+.\w+\.+[a-zA-Z0-9\/_]+)"
        source_data = self.env['website_cpo_index.cpo_website_source'].sudo().search([])
        data = source_data.filtered(lambda x: x.user_id != None)
        for i in data:
            if i.customer_source:
                url = re.search(reg, i.customer_source)
                if url:
                    if self.name in url.group():
                        if i.user_id and not (i.user_id.id in user_list):
                            user_list.append(i.user_id.id)
        return user_list

    @api.model
    def cpo_time_pd(self):
        today_8 = datetime.datetime.strptime(datetime.datetime.utcnow().strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
        return today_8.strftime('%Y-%m-%d %H:%M:%S')

    @api.depends('cpo_type.user_id')
    def _get_user_number(self):
        for s in self:
            user_list = s.search_users_func()
            s.user_number = len(user_list)

    @api.multi
    def cpo_search_users_btn(self):
        """
        查看当前记录有几个用户
        :return:
        """
        user_list = self.search_users_func()
        view_tree = self.env.ref('website_cpo_index.cpo_personal_center_tree_inherit')
        view_form = self.env.ref('personal_center.personal_center_form').id
        return {
            'name': _('Number of people'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'personal.center',
            'views': [(view_tree.id, 'tree'), (False, 'form')],
            # 'view_id': view_id.id,
            'domain': [('id', 'in', user_list)],
            'flags': {
                'form': {
                    'action_buttons': True
                }
            }
        }

    @api.multi
    def matching_website(self, value):
        """
        匹配网站
        :param value:
        :return:
        """
        # 匹配完整的网址
        reg = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)|([a-zA-Z]+.\w+\.+[a-zA-Z0-9\/_]+)"
        # 匹配简写（例如：www.baidu.com）
        reg2 = r'(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*'
        url_data = None
        try:
            get_url = re.search(reg, value)
            partner_data = self.search([])
            if value == '' or value == '/':
                pass
            if get_url:
                url_data = self.get_url_data_id(get_url, partner_data, reg2, value)
            else:
                get_url = re.search(reg2, value)
                url_data = self.get_url_data_id(get_url, partner_data, reg2, value)
            return url_data
        except Exception, e:
            _logger.error("Abnormal capture: %s" % e)
            return url_data

    def get_url_data_id(self, get_url, partner_data, reg2, value, url_data=None):
        for pd in partner_data:
            p_name = pd.name
            if not p_name:
                p_name = 'www.icloudfactory.com'
            if p_name:
                if (p_name in get_url.group()) or (get_url.group() in p_name) or (get_url.group() == p_name):
                    url_data = pd.id
                    break
        if not url_data:
            shorthand_url = re.search(reg2, value)
            url_data = self.get_url_search(shorthand_url)
            # if shorthand_url:
            #     g_url = shorthand_url.group()
            # else:
            #     g_url = None
            # vals = {
            #     'cpo_name': g_url,
            #     'name': g_url,
            #     'cpo_time': datetime.datetime.now()
            # }
            # shorthand_data = self.create(vals)
            # url_data = shorthand_data.id
        return url_data

    def get_url_search(self, reg):
        if reg:
            g_url = reg.group()
        else:
            g_url = None
        if not g_url:
            source = self.sudo().search([('name', 'in', ['www.icloudfactory.com'])])
            return source.id
        vals = {
            'cpo_name': g_url,
            'name': g_url,
            'cpo_time': datetime.datetime.now()
        }
        shorthand_data = self.create(vals)
        url_data = shorthand_data.id
        return url_data

    @api.multi
    def get_partner_source(self, user_id, current_url):
        url_id = None
        partner_id = self.env['personal.center'].sudo().search([('user_id', '=', user_id)])
        if partner_id:
            if partner_id.website_source:
                # url_data = self.matching_website(partner_id.website_source)
                url_data = self.matching_website(current_url)
                # source.customer_source = url_data
                url_id = url_data
                return url_id
            else:
                source_id = self.env['website_cpo_index.cpo_website_source'].sudo().search(
                    [('user_id', '=', partner_id.id)])
                if source_id:
                    source_data = source_id.filtered(lambda x: x.customer_related != None)
                    last_source = source_data[len(source_data)-1]
                    if last_source.cpo_source:
                        url = self.matching_website(last_source.cpo_source)
                        # data = self.search([('id', '=', url)])
                        partner_id.write({
                            'website_source': last_source.cpo_source
                        })
                        # website_source = data.name
                        url_id = url
                        return url_id
                    else:
                        if current_url:
                            partner_id.website_source = current_url
                            url_data = self.matching_website(current_url)
                            # url_id = url_data.id
                            url_id = url_data
                            return url_id
                else:
                    if current_url:
                        partner_id.website_source = current_url
                        url_data = self.matching_website(current_url)
                        url_id = url_data
                        return url_id


class CpoWebsiteSource(models.Model):
    """
    记录网站来源，例如来自百度的推广等。
    """

    _name = "website_cpo_index.cpo_website_source"
    _order = "sequence desc, id desc"
    cpo_list = {}

    SELECT_DEALWITH = [
        ('unprocessed', 'Unprocessed'),
        ('processed', 'Processed')
    ]

    @api.model
    def re_cpo_index_session_obj(self, session_res, url):
        if not session_res or not url:
            return self
        if session_res.keys()[0] not in self.cpo_list.keys():
            self.cpo_list[session_res.keys()[0]] = {}
        return self.re_cpo_index_update_url(session_res, url)

    @api.model
    def re_cpo_index_update_url(self, session_res, url):
        sess = session_res.keys()[0]
        u_time = session_res.values()[0]
        if url in self.cpo_list[sess].keys():
            self.cpo_list[sess][url].update({'update_time': u_time})
        else:
            self.cpo_list[sess] = {
                url: {'init_time': u_time}
            }
        return self

    @api.model
    def re_cpo_index_update_time(self, res_session, url):
        if self.cpo_list[res_session][url].get('update_time'):
            self.cpo_list[res_session][url]['init_time'] = self.cpo_list[res_session][url]['update_time']
        return self

    @api.model
    def re_cpo_index_check_data(self, res_session, url):
        self.re_cpo_index_clear_data()
        time_delta = self.set_system_parameter_key()
        if self.cpo_list.get(res_session):
            res_list = self.cpo_list.get(res_session)
            if res_list.get(url):
                res_url = res_list[url]
                if res_url.get('update_time'):
                    res_timedelta = res_url['update_time'] - res_url['init_time']
                    if res_timedelta < time_delta:
                        return False
                self.re_cpo_index_update_time(res_session, url)
                #self.cpo_list[res_session][url]['init_time'] = res_list['update_time']
        return True

    def cpo_session_time_out(self):
        """
        设置删除会话的时间
        :param vals:
        :return:
        """
        timeout = None
        cpo_key = 'time_out'
        sys_model = self.env['ir.config_parameter']
        key_data = sys_model.get_param('time_out')
        if not key_data:
            sys_model.set_param(cpo_key, 3600)
        return float(sys_model.get_param('time_out')) or 3600

    @api.model
    def re_cpo_index_clear_data(self):
        timeout_len = self.cpo_session_time_out()
        self.cpo_list = dict([(x[0],x[1]) for x in self.cpo_list.items() if time.time()-x[1].values()[0].values()[0] <= timeout_len ])

    @api.model
    def _cpo_set_time(self):
        now_time = datetime.datetime.now()
        return now_time

    sequence = fields.Integer(string='Sequence')
    user_id = fields.Many2one("personal.center", compute="_matching_users", string="Associated User", store=True)
    customer_source = fields.Char(related='user_id.website_source', string="Customer Source", store=True)
    session_id = fields.Many2one("cpo_session_association", string="Session ID")
    session_src = fields.Char(related='session_id.session_id', string='Session Src', store=True)
    user_name = fields.Char(related='session_id.user_name', string="User Name", store=True)
    customer_related = fields.Many2one("website_cpo_index.cpo_partner_source", string="Promotion source", compute="_change_source", store=True)
    cpo_source = fields.Char(string="Website Source")
    access_path = fields.Char(string="Access Path")
    cpo_ip = fields.Char(string="User IP")
    cpo_country = fields.Char(string="Country")
    cpo_city = fields.Char(string="City")
    cpo_time = fields.Datetime(string="Last update time", default=_cpo_set_time)
    deal_with = fields.Selection(SELECT_DEALWITH, string="Deal with", default="unprocessed", index=True)

    @api.model
    def cpo_time_pd(self):
        today_8 = datetime.datetime.strptime(datetime.datetime.utcnow().strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
        return today_8.strftime('%Y-%m-%d %H:%M:%S')

    @api.one
    @api.depends('session_id', 'session_id.customer_name', 'session_id.user_id')
    def _matching_users(self):
        if self.session_id.user_id != self.env.ref("base.public_user").id:
            self.user_id = self.session_id.customer_name.id

    @api.one
    @api.depends('user_name')
    def _change_source(self):
        for ui in self:
            user_id = ui.user_id
            if user_id:
                # if user_id.website_source:
                # if ui.customer_related:
                #     # url_id = self.env['website_cpo_index.cpo_partner_source'].matching_website(user_id.website_source)
                #     url_id = self.env['website_cpo_index.cpo_partner_source'].matching_website(ui.cpo_source)
                #     ui.customer_related = url_id
                # else:
                    # url_id = self.env['website_cpo_index.cpo_partner_source'].get_partner_source(user_id.user_id.id, ui.cpo_source)
                    # url_id = self.env['website_cpo_index.cpo_partner_source'].matching_website(ui.cpo_source)
                    # ui.customer_related = url_id
                url_id = self.env['website_cpo_index.cpo_partner_source'].matching_website(ui.cpo_source)
                ui.customer_related = url_id
            else:
                url_id = self.env['website_cpo_index.cpo_partner_source'].matching_website(ui.cpo_source)
                ui.customer_related = url_id


    def set_system_parameter_key(self):
        """
        将时间间隔设置为系统参数，可以在系统参数中设定
        :return:
        """
        sys_value = None
        cpo_key = 'website_source_record_key'
        sys_model = self.env['ir.config_parameter']
        key_data = sys_model.get_param(cpo_key)
        if not key_data:
            sys_model.set_param(cpo_key, 60)
        return float(sys_model.get_param(cpo_key)) or 3600

    @api.multi
    def get_data_create(self, vals, url):
        res_session = vals.keys()[0]
        vals = vals.values()[0]
        domain = [
           # ('user_id', '=', vals.get('user_id')),
           ('user_name', '=', vals.get('user_name') or 'Public user'),
           ('cpo_source', '=', vals.get('cpo_source') or False),
           ('access_path', '=', vals.get('access_path') or False),
           ('cpo_ip', '=', vals.get('cpo_ip') or False),
           ('cpo_city', '=', vals.get('cpo_city') or ''),
           ('cpo_country', '=', vals.get('cpo_country') or ''),
           ('session_id', '=', hash(vals.get('session_id')) or False)
        ]
        if not self.re_cpo_index_check_data(res_session, url):
            return False
        if self.get_data_search(domain):
            new_ids = self.create(vals)
            return new_ids
        else:
            cpo_ids = self.search(domain).sorted(key=lambda r: r.id,reverse=True)
            cpo_ids[1:].unlink()
            cpo_ids[0].sudo().update({'cpo_time':fields.Datetime.now()})
            return cpo_ids[0]

    @api.multi
    def get_data_search(self, vals):
        flag = False
        try:
            cpo_model = self.env['ir.model'].search([('model', '=', 'website_cpo_index.cpo_website_source')])
            if cpo_model:
                data = self.search(vals)
                if len(data) < 1:
                    flag = True
            else:
                return flag
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return flag

    # @api.model
    # def handle_sudo_security(self, model_obj):
    #     obj_pool = None
    #     if model_obj == 'self':
    #         obj_pool = self.sudo()
    #     else:
    #         obj_pool = self.env[model_obj].sudo()
    #     return obj_pool

class PersonalCenter(models.Model):
    """
    继承个人中心，添加用户来源，当存在时不更新，不存在时更新
    """
    _inherit = 'personal.center'

    website_source = fields.Char(string='Customer source')
    quote_related = fields.One2many('cpo_pcb_and_pcba_record', 'user_name', string="Quotation Association")
    source_related = fields.One2many('website_cpo_index.cpo_website_source', 'user_id', string="Source Association")
    quote_record = fields.Integer(string="Number of quotation ", compute="_get_quotation_number", default=0)
    source_number = fields.Integer(string="Number of source", compute="_get_source_number", default=0)

    @api.one
    @api.depends('quote_related')
    def _get_quotation_number(self):
        """
        在客户中心显示报价记录数量
        :return:
        """
        self.quote_record = len(self.quote_related)

    def get_quotation_record(self):
        """
        在客户个人中心查看相应的报价记录
        :return:
        """
        user_list = self.quote_related.ids
        view_tree = self.env.ref('website_cpo_index.cpo_quotation_record_base_tree')
        return {
            'name': _('Quotation number'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'cpo_pcb_and_pcba_record',
            'views': [(view_tree.id, 'tree'), (False, 'form')],
            'view_id': False,
            'domain': [('id', 'in', user_list)],
            'flags': {
                'form': {
                    'action_buttons': True
                }
            }
        }

    @api.one
    @api.depends('source_related')
    def _get_source_number(self):
        """
        在客户中心显示访问记录数量
        :return:
        """
        self.source_number = len(self.source_related)

    def get_source_record(self):
        """
        在客户个人中心查看相应的访问记录
        :return:
        """
        user_list = self.source_related.ids
        return {
            'name': _('Source number'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'website_cpo_index.cpo_website_source',
            'views': [(False, 'tree'), (False, 'form')],
            'view_id': False,
            'domain': [('id', 'in', user_list)],
            'flags': {
                'form': {
                    'action_buttons': True
                }
            }
        }

class CpoPartnerSourceData(models.Model):
    """
    记录网站来源，例如来自百度的推广等。
    """

    _name = "website_cpo_index.all_partner_source"
    _order = "sequence desc, id desc"

    SELECTION_TYPE = [
        ('search_engine', 'Search engine'),
        ('facebook', 'Facebook')
    ]

    @api.model
    def _cpo_set_time(self):
        now_time = datetime.datetime.now()
        return now_time

    sequence = fields.Integer(string='Sequence')
    site_name = fields.Many2one("website_cpo_index.cpo_partner_source", string="Site Name")
    cpo_name = fields.Char(string="Website Address")
    session_id = fields.Many2one("cpo_session_association", string="Session ID")
    cpo_time = fields.Datetime(string="Last update time", default=_cpo_set_time)
    # type = fields.Many2one('routing_parameter.link_rule', string="Source type")

    def all_source_data(self, vals):
        # self.routing_analysis(vals.get('cpo_name'))
        try:
            site_data = self.env['website_cpo_index.cpo_partner_source'].matching_website(vals.get('cpo_name'))
            if site_data != vals.get('site_name'):
                vals['site_name'] = site_data
            values = [
                ('site_name', '=', vals.get('site_name')),
                ('cpo_name', '=', vals.get('cpo_name')),
                ('session_id', '=', vals.get('session_id'))
            ]
            vals.update({
                'cpo_time': datetime.datetime.now()
            })
            data = self.search(values)
            if not data:
                self.create(vals)
        except Exception, e:
            _logger.error("Error message: %s" % e)
            return True

    def routing_analysis(self, url):
        """
        分析路由的关键字
        :param url:
        :return:
        """
        parameter_dict = None
        name_one = 'https://www.icloudfactory.com'
        name_two = 'https://www.chinapcbone.com'
        cpo_analysis = urlparse.urlsplit(url)  # 解析路由
        cpo_domain_name = cpo_analysis.netloc  # 获取域名
        selate_site_name = self.env['website_cpo_index.cpo_partner_source'].matching_website(cpo_domain_name)
        cpo_parameter = cpo_analysis.query  # 获取参数
        if not cpo_parameter:
            return False
        parameter_dict = dict([(key, value[0]) for key, value in urlparse.parse_qs(cpo_parameter).items()])
        if cpo_domain_name in name_one or name_one in cpo_domain_name:
            # 来之内部
            for key in parameter_dict:
                self.env['routing_parameter.internal_keyword'].create({
                    'key': key,
                    'value': parameter_dict[key],
                    'domain_name': cpo_domain_name,
                    'site_name': selate_site_name,
                    'cpo_time': fields.Datetime.now()
                })
        elif cpo_domain_name in name_two or name_two in cpo_domain_name:
            # 来自内部
            for key in parameter_dict:
                self.env['routing_parameter.internal_keyword'].create({
                    'key': key,
                    'value': parameter_dict[key],
                    'domain_name': cpo_domain_name,
                    'site_name': selate_site_name,
                    'cpo_time': fields.Datetime.now()
                })
        else:
            # 来自外部
            for key in parameter_dict:
                self.env['routing_parameter.external_keyword'].create({
                    'key': key,
                    'value': parameter_dict[key],
                    'domain_name': cpo_domain_name,
                    'site_name': selate_site_name,
                    'cpo_time': fields.Datetime.now()
                })



class CPOWebsiteTag(models.Model):
    """
    推广分类，例如邮箱，常规网站的
    """

    _name = "website_cpo_index.website_tag"
    _order = "id desc"

    name = fields.Char(string="Tag name")
    site_address = fields.Char(string="Site address")
    tag_ids = fields.Many2many('website_cpo_index.cpo_partner_source', 'tag_partner_rel', 'partner_id', 'tag_id', string='Tag')


