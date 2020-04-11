# -*- coding: utf-8 -*-

import logging, requests, json
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.http import Root, Response
from odoo.addons.web.controllers.main import Session
from odoo.addons.website_cpo_sale.controllers.main import WebsiteSourceHome as Home
from odoo.addons.website_cpo_sale.controllers.main import Inherit_CPOwebsite_account as MyHome
from odoo.addons.website_cpo_sale.controllers.main import Inherit_WebsiteSaleElectron as Cart
from odoo.addons.website_cpo_sale.controllers.main import cpo_inherit_WebsiteSale as PCBA
from odoo.addons.website_cpo_sale.controllers.stenil_quotation import StentcilWebsiteSale as SteelMesh
from odoo.addons.website_cpo_sale.controllers.pcb_quotation import InheritWebsiteSalePCB as PCB

_logger = logging.getLogger(__name__)


class SessionBehaviorSource(object):
    # ir.module.module
    # 先检查进来的session有没有记录
    def CheckRecord(self):
        return request.env['cpo_session_association'].sudo().CheckSession(request.session.sid)

    # 记录 没有的Session
    def RegistrationSession(self):
        value = self.GoogleIuquire(ip=request.httprequest.remote_addr)
        value = {
            'session_ip': value.get('ip') or request.httprequest.remote_addr,
            'session_city': False or value.get('city').encode('utf-8'),
            'session_country': False or value.get('country_name').encode('utf-8'),
            'session_id': request.session.sid,
            'user_id': request.env.user.id,
            'user_name': request.env.user.name,
        }
        return value

    # 使用Google 通过ip 查出地址
    def GoogleIuquire(self, ip='127.0.0.1'):
        try:
            url = 'https://api.ipdata.co/' + ip + '/zh-CN?api-key=711bdbbbdb292be37d625a22bf9706a435764be5dc8e527322c682c8'
            return json.loads(requests.get(url).content)
        except Exception as e:
            _logger.error(e.message)
            return {}

    # 所有路劲进行统一检查 只查询 或 记录session
    def CheckOrCreateSession(self):
        session_obj = request.env['cpo_session_association']
        value = self.CheckRecord()  # 返回 session 对象
        if not value:
            value = self.RegistrationSession()  # 返回是 Google查询的信息
            value = session_obj.sudo().CreateSession(value)  # 返回 session 对象
        return value

    # 检查来源 没有创建 有返回对象 与session表没有 直接关系
    def CheckOrCreateSource(self, session):
        come = request.httprequest.environ.get('HTTP_REFERER')
        x_id, come = request.env['website_cpo_index.cpo_partner_source'].sudo().ParsingWebsite(come)
        return request.env['website_cpo_index.all_partner_source'].sudo().ParsingWebsiteLine(x_id, come, session.id)

    # 登记行为
    def RecordBehavior(self, session, source):
        value = {
            'session': session,
            'source': source,
            'path': request.httprequest.environ.get('PATH_INFO'),
        }
        request.env['website_cpo_index.cpo_website_source'].sudo().CheckBehavior(value)

    # 主控函数
    def MasterControl(self):
        session = self.CheckOrCreateSession()
        source = self.CheckOrCreateSource(session)
        self.RecordBehavior(session, source)


class CRMHome(Home):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        res = super(Home, self).web_login(redirect, *args, **kw)
        SessionBehaviorSource().MasterControl()
        # 在登入之前一定是先进行session的记录
        if request.params['login_success']:
            value = SessionBehaviorSource().CheckRecord()
            request.env['cpo_session_association'].sudo().UpdateAssociatedCustomer(user_id=request.env.user.id, session=value)
        return res

    @http.route()
    def page(self, page, **kw):
        SessionBehaviorSource().MasterControl()
        return super(Home, self).page(page, **kw)

    @http.route()
    def web_auth_signup(self, *args, **kw):
        SessionBehaviorSource().MasterControl()
        return super(Home, self).web_auth_signup(*args, **kw)


class CRMMyHome(MyHome):

    @http.route()
    def account(self, **kw):
        SessionBehaviorSource().MasterControl()
        return super(MyHome, self).account(**kw)


class CRMCart(Cart):

    @http.route()
    def cart(self, **post):
        SessionBehaviorSource().MasterControl()
        return super(Cart, self).cart(**post)


class CRMPCBA(PCBA):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, source=None, type=None, bom_id=False, ufile=None, **post):
        SessionBehaviorSource().MasterControl()
        return super(PCBA, self).shop(page=page, category=category, search=search, ppg=ppg, source=source, type=type, bom_id=bom_id, ufile=ufile, **post)


class CRMPCB(PCB):

    @http.route()
    def old_pcb(self, page=0, category=None, search='', ppg=False, source=None, type=None, ufile=None, **post):
        SessionBehaviorSource().MasterControl()
        return super(PCB, self).old_pcb(page=page, category=category, search=search, ppg=ppg, source=source, type=type, ufile=ufile)


class CRMSteelMesh(SteelMesh):

    @http.route()
    def stencil(self, source=None, **post):
        SessionBehaviorSource().MasterControl()
        return super(SteelMesh, self).stencil(source=source, **post)


class UserExit(Session):

    @http.route()
    def logout(self, redirect='/web'):
        res = super(UserExit, self).logout(redirect)
        r = request.httprequest
        response = werkzeug.utils.redirect(res, 302)
        # response = r.app.get_response(r, response, explicit_session=False)
        # root
        return res

# test_root = Root()

# class InheritRoot(Root):
#
#     def __init__(self):
#         self._loaded = False
#
#     def get_response(self, httprequest, result, explicit_session):
#         if isinstance(result, Response) and result.is_qweb:
#             try:
#                 result.flatten()
#             except(Exception) as e:
#                 if request.db:
#                     result = request.registry['ir.http']._handle_exception(e)
#                 else:
#                     raise
#
#         if isinstance(result, basestring):
#             response = Response(result, mimetype='text/html')
#         else:
#             response = result
#
#         # save to cache if requested and possible
#         if getattr(request, 'cache_save', False) and response.status_code == 200:
#             response.freeze()
#             r = response.response
#             if isinstance(r, list) and len(r) == 1 and isinstance(r[0], str):
#                 request.registry.cache[request.cache_save] = {
#                     'content': r[0],
#                     'mimetype': response.headers['Content-Type'],
#                     'time': time.time(),
#                 }
#
#         if httprequest.session.should_save:
#             if httprequest.session.rotate:
#                 self.session_store.delete(httprequest.session)
#                 httprequest.session.sid = self.session_store.generate_key()
#                 httprequest.session.modified = True
#             self.session_store.save(httprequest.session)
#         # We must not set the cookie if the session id was specified using a http header or a GET parameter.
#         # There are two reasons to this:
#         # - When using one of those two means we consider that we are overriding the cookie, which means creating a new
#         #   session on top of an already existing session and we don't want to create a mess with the 'normal' session
#         #   (the one using the cookie). That is a special feature of the Session Javascript class.
#         # - It could allow session fixation attacks.
#         if not explicit_session and hasattr(response, 'set_cookie'):
#             response.set_cookie('session_id', httprequest.session.sid, max_age=90 * 24 * 60 * 60)
#
#         return response
#     # def __init__(self):
#     #     root.__init__()
#
#     # @http.root
#     @classmethod
#     def dispatch(cls, environ, start_response):
#         return super(InheritRoot, cls).dispatch(environ, start_response)
#
#     # @http.root
#     @classmethod
#     def get_response(cls, httprequest, result, explicit_session):
#         a = 1
#         return super(InheritRoot, cls).get_response(httprequest, result, explicit_session)
#
#
# # InheritRoot(root)

