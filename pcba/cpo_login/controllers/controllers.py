# -*- coding: utf-8 -*-
import odoo
from odoo import http, tools, _
from odoo.addons.web.controllers import main
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class CpoLogin(main.Home):
    """
    继承Web模块的class（Home），增加一个登录的路径
    """

    @http.route('/quote/login', type='http', auth="none")
    def cpo_website_quote_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        try:
            type = None
            if kw.get('src'):
                if kw.get('type'):
                    type = 'type=' + kw.get('type')
                    redirect = kw.get('src') + '?' + type + '&login=true'
                else:
                    redirect = kw.get('src') + '?login=true'
                http.redirect_with_hash(redirect)
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)

        if request.httprequest.method in ['POST', 'GET']:
            old_uid = request.uid
            if request.params.get('login') and request.params.get('password'):
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                if uid is not False:
                    request.params['login_success'] = True
                    if not redirect:
                        redirect = '/web'
                    return http.redirect_with_hash(redirect)
                request.uid = old_uid
                values['error'] = _('Email or password does not match. Please try again or <a target="_parent" href="/web/reset_password" style="text-decoration:underline">reset your password</a>.')
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        response = request.render('cpo_login.cpo_login_layout', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    @http.route('/check/login', type='json', auth='public', website=True)
    def cpo_check_quote_login(self, redirect=None, **kw):
        """
        验证登录，若果登录名，密码正确，就跳转
        :param redirect:
        :param kw:
        :return:
        """
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method in ['POST', 'GET']:
            old_uid = request.uid
            if request.params.get('login') and request.params.get('password'):
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                if uid is not False:
                    request.params['login_success'] = True
                    values['error'] = None
                    return values
                request.uid = old_uid
                values['error'] = _('Email or password does not match. Please try again or <a target="_parent" href="/web/reset_password" style="text-decoration:underline">reset your password</a>.')
            else:
                values.update({
                    'error': 'Account or password cannot be empty!',
                })
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')
        if values.get('error'):
            return {
                'error': request.env['ir.ui.view'].render_template(
                    'cpo_login.cpo_login_error', values)
            }



    @http.route('/quote/test', type='http', auth="none")
    def cpo_website_test(self, redirect=None, **kw):
        values = {}
        return request.render('cpo_login.login_template_test', values)

    def get_modules_order(self):
        pass
# class CpoLogin(http.Controller):
#     @http.route('/cpo_login/cpo_login/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpo_login/cpo_login/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpo_login.listing', {
#             'root': '/cpo_login/cpo_login',
#             'objects': http.request.env['cpo_login.cpo_login'].search([]),
#         })

#     @http.route('/cpo_login/cpo_login/objects/<model("cpo_login.cpo_login"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpo_login.object', {
#             'object': obj
#         })