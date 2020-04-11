# -*- coding: utf-8 -*-

import logging, random, werkzeug, urllib, os
from ..controllers.customer_country import IPCountry
from datetime import datetime, timedelta
from time import time
from urlparse import urljoin
from base64 import b64encode as e64
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.http import request

_logger = logging.getLogger(__name__)


def random_token(string=False):
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    if string:
        return ''.join(random.SystemRandom().choice(chars) for _ in pycompat.range(20))
    else:
        return random.choice(chars)


def time_utc(**kwargs):
    now = datetime.utcfromtimestamp(time()) + timedelta(**kwargs)
    return fields.Datetime.to_string(now)


class PersonalCenter(models.Model):
    _name = 'personal.center'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Customer Personal Center'

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    def _default_category(self):
        return self.env['res.partner.category'].browse(self._context.get('category_id'))

    name = fields.Char('Name', size=64, compute='_get_user_name', store=True)
    user_id = fields.Many2one('res.users', auto_join=True, index=True, ondelete='cascade', readonly=True, string='Client')
    partner_id = fields.Many2one('res.partner', auto_join=True, index=True, ondelete='cascade', readonly=True, string='Client')
    type = fields.Selection([('contact', 'Contact'),
                             ('invoice', 'Invoice address'),
                             ('delivery', 'Shipping address'),
                             ('other', 'Other address')], string='Address Type', default='contact',
                            related='partner_id.type',
                            help="Used to select automatically the right address according to the context in sales and purchases documents.")
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    zip = fields.Char(change_default=True, related='partner_id.zip')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', related='partner_id.state_id')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related='partner_id.country_id')
    vat = fields.Char(string='TIN', help="Tax Identification Number. "
                                         "Fill it if the company is subjected to taxes. "
                                         "Used by the some of the legal statements.", related='partner_id.vat')
    website = fields.Char(help="Website of Partner or Company", related='partner_id.website')
    category_id = fields.Many2many('res.partner.category', column1='partner_id', related='partner_id.category_id',
                                   column2='category_id', string='Tags', default=_default_category)
    is_company = fields.Boolean(string='Is a Company', default=False, related='partner_id.is_company',
                                help="Check if the contact is a company, otherwise it is a person")
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', related='partner_id.commercial_partner_id')
    company_type = fields.Selection(string='Company Type', related='partner_id.company_type',
                                    selection=[('person', 'Individual'), ('company', 'Company')])
    image = fields.Binary("Image", attachment=True, help="This field holds the image used as avatar for this contact, limited to 1024x1024px", related='partner_id.image')
    image_medium = fields.Binary("Medium-sized image", attachment=True, related='partner_id.image_medium',
                                 help="Medium-sized image of this contact. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True, related='partner_id.image_small',
                                help="Small-sized image of this contact. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
    function = fields.Char(string='Job Position', related='partner_id.function')
    phone = fields.Char(related='partner_id.phone')
    fax = fields.Char(related='partner_id.fax')
    mobile = fields.Char(related='partner_id.mobile')
    email = fields.Char(related='partner_id.email')
    title = fields.Many2one('res.partner.title', related='partner_id.title')
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang, related='partner_id.lang',
                            help="If the selected language is loaded in the system, all documents related to "
                                 "this contact will be printed in this language. If not, it will be English.")
    active = fields.Boolean(default=True, related='partner_id.active')
    child_ids = fields.One2many('res.partner', 'parent_id', string='Contacts', domain=[('active', '=', True)], related='partner_id.child_ids')  # force "active_test" domain to bypass _search() override
    color = fields.Integer(string='Color Index', compute='_compute_active_type', store=True)
    supplier = fields.Boolean(string='Is a Vendor', related='partner_id.supplier',
                              help="Check this box if this contact is a vendor. "
                                   "If it's not checked, purchase people will not see it when encoding a purchase order.")
    customer = fields.Boolean(string='Is a Customer', default=True, related='partner_id.customer',
                              help="Check this box if this contact is a customer.")
    ref = fields.Char(string='Internal Reference', related='partner_id.ref')
    industry_id = fields.Many2one('res.partner.industry', 'Sector of Activity', related='partner_id.industry_id')
    company_id = fields.Many2one('res.company', 'Company', default=_default_company, related='partner_id.company_id')
    pcb_order = fields.Integer(compute='_compute_order', string='PCB Order', store=True)
    pcba_order = fields.Integer(compute='_compute_order', string='PCBA Order', store=True)
    stencil_order = fields.Integer(compute='_compute_order', string='Stencil Order', store=True)
    paid = fields.Float(digits=(16, 2), string='Paid', compute='_compute_paid', store=True)
    balance = fields.Float('Account Balance', digits=(16, 5), readonly=True)
    paid_bool = fields.Boolean('Paid')  # 此属性作用激活_compute_paid
    word = fields.Char('Password')
    activation_type = fields.Selection([('Activation', 'Activation'),
                                        ('Inactivated', 'Inactivated')], string='Whether the account is activated', default='Inactivated', compute='_compute_active_type', store=True)
    country = fields.Char('Country', compute='_compute_country', store=True, translate=True)
    session_country = fields.Char('Country')
    client_id_code = fields.Char('Client Id Code', compute='_get_client_id_code', store=True, index=True)
    discount_amount = fields.Float('Discount Amount', default=0.0)
    sale_client_code = fields.Char('Internal Client Code', groups="sales_team.group_sale_salesman")

    @api.one  # C YY MM DD XXX
    @api.depends('user_id')
    def _get_client_id_code(self):
        x_str = 'C' + ''.join(self.create_date.split('-'))[2:8]
        num = self.search([('client_id_code', 'like', x_str)])
        num = '1' if not num else str(int(max(num).client_id_code[-3:]) + 1)
        if len(num) == 1:
            self.client_id_code = x_str + '00' + num
        elif len(num) == 2:
            self.client_id_code = x_str + '0' + num
        else:
            self.client_id_code = x_str + num

    # 验证是否激活
    @api.depends('word', 'user_id')
    def _compute_active_type(self):
        for x_id in self:
            x_id.activation_type = 'Inactivated' if x_id.word else 'Activation'
            x_id.color = 1 if x_id.word else 0

    @api.depends('partner_id.country_id', 'session_country')
    def _compute_country(self):
        for x_id in self:
            x_id.country = x_id.session_country if not x_id.country_id else x_id.country_id.name

    @api.multi
    # 返回相应内容
    def get_correspond_views(self):
        if self._context.get('value') == 'pcb':
            return self._get_action('personal_center.act_order')
        elif self._context.get('value') == 'pcba':
            return self._get_action('personal_center.act_order')
        elif self._context.get('value') == 'stencil':
            return self._get_action('personal_center.act_order')
        elif self._context.get('value') == 'paid':
            return self._get_action('personal_center.act_paid')

    @api.multi
    # 进行内容筛选
    def _get_action(self, action_xmlid, value=False):
        action = self.env.ref(action_xmlid).read()[0]
        if self._context.get('value') == 'pcb':
            action['domain'] = [('product_type', 'not in', ('PCBA', 'Stencil')),
                                ('partner_id', '=', self.partner_id.id)]
            action['display_name'] = _('PCB Order')
        elif self._context.get('value') == 'pcba':
            action['domain'] = [('product_type', '=', 'PCBA'),
                                ('partner_id', '=', self.partner_id.id)]
            action['display_name'] = _('PCBA Order')
        elif self._context.get('value') == 'stencil':
            action['domain'] = [('product_type', '=', 'Stencil'),
                                ('partner_id', '=', self.partner_id.id)]
            action['display_name'] = _('Stencil Order')
        elif self._context.get('value') == 'paid':
            action['domain'] = [('state', '=', 'paid'),
                                ('partner_id', '=', self.partner_id.id)]
            action['display_name'] = _('Paid')
        return action

    @api.one
    @api.depends('partner_id', 'paid_bool')
    # 统计已付款了多少钱
    def _compute_paid(self):
        invoice = self.env['account.invoice'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'paid')])
        self.paid = sum(x.amount_total for x in invoice)

    @api.one
    @api.depends('partner_id.sale_order_ids', 'partner_id')
    # 统计 pcb pcba 钢网的订单
    def _compute_order(self):
        order = self.partner_id.sale_order_ids
        try:
            self.pcb_order = len(order.filtered(lambda x: x.product_type not in ['PCBA', 'Stencil']).ids)
            self.pcba_order = len(order.filtered(lambda x: x.product_type == 'PCBA').ids)
            self.stencil_order = len(order.filtered(lambda x: x.product_type == 'Stencil').ids)
        except Exception as e:
            _logger.warning(e.message)
            self.pcb_order = 0
            self.pcba_order = 0
            self.stencil_order = 0

    @api.one
    @api.depends('user_id', 'user_id.name')
    # 映射客户名字
    def _get_user_name(self):
        if not self.user_id:
            return False
        self.name = self.user_id.name

    @api.multi
    def get_discount_amount(self, discount):
        self.discount_amount += discount
        return True

    @api.multi
    # 放回一个编辑视图
    def open_partner(self):
        self.ensure_one()
        address_form_id = self.env.ref('base.view_partner_address_form').id
        value = {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'views': [(address_form_id, 'form')],
            'res_id': self.partner_id.id,
            'target': 'new',
            'flags': {
                'form': {
                    'action_buttons': True
                }
            }
        }
        return value

    @api.multi
    # 前端调用客户个人订单接口
    def get_partner(self, partner_id, value):
        return self.GetPartnerOrder(partner_id, value)

    def GetPartnerOrder(self, partner_id, value):
        orders = self.env['sale.order'].sudo().search([('message_partner_ids', 'child_of', partner_id.commercial_partner_id.ids)])
        x_dict = {
            'qty': {
                'ur_qty': len(orders.filtered(lambda x: x.state in ['wait_confirm', 'sent', 'sale'])),
                'py_qty': len(orders.filtered(lambda x: x.state == 'wait_payment')),
                'm_qty': len(orders.filtered(lambda x: x.state in ['wait_make', 'manufacturing'])),
                'd_qty': len(orders.filtered(lambda x: x.state in ['wait_delivery', 'wait_receipt'])),
                'c_qty': len(orders.filtered(lambda x: x.state == 'complete'))
            }
        }
        if value == 'under_review':
            x_dict.update({'order': orders.filtered(lambda x: x.state in ['wait_confirm', 'sent', 'sale'])})
        elif value == 'manufacturing':
            x_dict.update({'order': orders.filtered(lambda x: x.state in ['wait_make', 'manufacturing'])})
        elif value == 'delivery':
            x_dict.update({'order': orders.filtered(lambda x: x.state in ['wait_delivery', 'wait_receipt'])})
        elif value == 'completed':
            x_dict.update({'order': orders.filtered(lambda x: x.state == 'complete')})
        elif value == 'awaiting_payment':
            x_dict.update({
                'invoice_qty': self.env['account.invoice'].sudo().search([
                    ('type', 'in', ['out_invoice', 'out_refund']),
                    ('state', 'in', ['open', 'paid', 'cancel']),
                    ('message_partner_ids', 'child_of', partner_id.commercial_partner_id.ids)
                ])
            })
        return x_dict

    @api.model
    def create(self, vals):
        # 这里要改为注册时候 使用 后台创建的不用触发
        vals['session_country'] = IPCountry().conutry(request=request)
        if ('user_id' not in vals.keys() or not vals.get('user_id')) and 'partner_id' in vals.keys():
            user_id = self.env['res.users'].search([('partner_id', '=', vals.get('partner_id'))]).id
            vals.update({'user_id': user_id})
        return super(PersonalCenter, self).create(vals)

    # 前端展示 产品状态数据
    def GetMakeState(self, client, order_id=False):
        return self.get_product_state(client, order_id=order_id)

    def get_product_state(self, client, order_id=False):
        if order_id:
            return self.env['sale.order'].browse(int(order_id)).circuit_ids
        value = {}
        order = client.sale_order_ids.filtered(lambda x: x.state in ['manufacturing', 'wait_make'])
        for x_id in order:
            x_str = 'No Information' if not x_id.circuit_ids else x_id.circuit_ids[-1].name
            value.update({
                x_id.id: x_str
            })
        return value

    # # 前端调用 工艺流程问题
    # def get_interface_flow(self, partner_id):
    #     return self.sudo().ShowProductFlow(partner_id)
    #
    # def ShowProductFlow(self, partner_id):
    #     order = self.env['sale.order'].sudo().search([('partner_id', '=', int(partner_id)),
    #                                                   ('state', 'in', ('manufacturing', 'wait_delivery', 'wait_receipt', 'complete'))])
    #     value = {
    #         'PCB': order.filtered(lambda x: x.product_type != 'PCBA' and x.quotation_line),
    #         'PCBA': order.filtered(lambda x: x.product_type == 'PCBA' and not x.quotation_line),
    #         'ALL': order.filtered(lambda x: x.product_type == 'PCBA' and x.quotation_line),
    #     }
    #     return value


class InheritResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    # 创建一个新用户的时候 也创建一条客户中心的记录
    def create(self, vals):
        res = super(InheritResUsers, self).create(vals)
        if res.share:
            self.env['personal.center'].create({'user_id': res.id, 'partner_id': res.commercial_partner_id.id})
        return res

    @api.multi
    # 当勾选的门户触发时
    def write(self, vals):
        res = super(InheritResUsers, self).write(vals)
        string = 'in_group_' + str(self.env.ref('base.group_portal').id)
        if string in vals.keys():
            self.update_center(self.id, vals.get('in_group_9'))
        return res

    @api.multi
    def unlink(self):
        parent_list = []
        for x_id in self:
            parent_list.append(x_id.partner_id.ids)
        res = super(InheritResUsers, self).unlink()
        for x_list in parent_list:
            self.env['res.partner'].browse(x_list).unlink()
        return res

    # 如果这个门户不存在于personal.center中 进行创建
    def update_center(self, user_id, group_id):
        center_id = self.env['personal.center'].search([('user_id', '=', user_id)])
        if group_id and not center_id:
            user_id = self.browse(user_id)
            self.env['personal.center'].create({'user_id': user_id.id, 'partner_id': user_id.commercial_partner_id.id})
        return True

    # 前端调用 注册
    def Enrolment(self, email, password=False):
        return self.sudo().GetVerification(email, password=password)

    def GetVerification(self, email, password=False):
        users = self.search([('login', '=', email), ('active', '=?', False)])
        if not password and self:
            users = self
        expiration = time_utc(hours=+1)
        users.mapped('partner_id').SignupPrepare(password, signup_type="reset", expiration=expiration)
        template = False
        if not template:
            template = self.env.ref('personal_center.mail_activation_template1')
        assert template._name == 'mail.template'
        if not self and password:
            users.write({'active': False})
        for user in users:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
        return True

    @api.multi
    def get_signup_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if self.env.context.get('signup_valid') and not self.user_ids:
            self.signup_prepare()
        route = 'email_verification'
        query = {'token': self.signup_token}
        res = urljoin(base_url, "/web/%s?%s" % (route, werkzeug.url_encode(query)))
        return res


class InheritPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def SignupPrepare(self, password, signup_type="signup", expiration=False):
        for partner in self:
            if (expiration or not partner.signup_valid) and password:
                token = self.encryption(password, partner)
                token = urllib.quote(token)
                while self._signup_retrieve_partner(token):
                    token = random_token()
                partner.write({'signup_token': token, 'signup_type': signup_type, 'signup_expiration': expiration})
            elif not password:
                partner.write({'signup_expiration': expiration})
        return True

    def encryption(self, password, partner):
        cen = self.env['personal.center'].search([('partner_id', '=', partner.id)])
        token = random_token(string=True)
        password = e64(password)
        db = e64(self.env.cr.dbname)
        token = token[:5] + password + token[5:] + '&' + str(cen.id) + '&' + db[:3] + random_token() + db[3:]
        cen.update({'word': len(password)})
        return token


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        res = super(InheritAccountInvoice, self).write(vals)
        if self and vals.get('state') == 'paid':
            paid = self.env['personal.center'].search([('partner_id', '=', self.partner_id.id)])
            paid.update({'paid_bool': True if not paid.paid_bool else False})
        return res


class InheritSalesOrder(models.Model):
    _inherit = 'sale.order'

    client_id = fields.Many2one('personal.center', 'Client', auto_join=True, compute='_depends_client', store=True)
    country = fields.Char(string='Country', related='client_id.country')

    @api.depends('partner_id')
    def _depends_client(self):
        for x_id in self:
            cen_id = self.env['personal.center'].search([('partner_id', '=', x_id.partner_id.id)]).id
            x_id.client_id = cen_id

    @api.one
    @api.multi
    def write(self, vals):
        partner_id, discount = self.partner_id.id, self.discount_total
        if vals.get('state') == 'wait_make':
            self.env['personal.center'].search([('partner_id', '=', partner_id)]).get_discount_amount(discount)
        return super(InheritSalesOrder, self).write(vals)

