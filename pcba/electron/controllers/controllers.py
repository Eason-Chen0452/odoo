# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website.controllers.main import QueryURL
import re
import operator
from odoo.addons.website.models.website import slug
from ..models.electron_relation import WEBSITE_SEARCH_FIELDS

PPG = 40  # Products Per Page
PPR = 4   # Products Per Row

class Electron(http.Controller):
    # @http.route('/electron/electronic/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    # @http.route(['/electron/get_product_len'], type='json', auth="public", methods=['post'], website=True)
    def get_product_len(self, category=None, title=None, filter=None):
        values = {}
        for row in filter:
            key = row.keys()[0]
            value = row.values()
            if key in values.keys():
                values.update({key: row.values()+values[key]})
            else:
                values[key] = value
        disk_rel =http.request.env['electron.disk_center']
        Product = http.request.env['electron.origin_data']
        category_obj = http.request.env['electron.electronic']
        category_str = category_obj.search([('id','=',category)]).mapped("name")
        fields_rel_dict = disk_rel.get_disk_rel(type=category_str)
        category = re.search("\d*",category)
        category = int(category.group()) if category else 0
        domain = [ ('p_type','=',category)]
        for row in values.keys():
            if row != None:
                domain += [ (fields_rel_dict.get(row),'in', values.get(row)) ]# if fields_rel_dict.get(row) else [('id', =, '-1')]
        ids = Product.search(domain).mapped("id")
        count = Product.search_count(domain)
        return {'ids':ids,'count':count}

    # @http.route([
    #     '/electron/electronic/category/<model("electron.electronic"):category>/product/add',
    #     '/electron/electronic/category/<model("electron.electronic"):category>/product/<string:product_new>',
    #  ], type='http', auth='user', website=True)
    def add_product(self, category=None, product_new=None, **post):
        post.update({'product_new': product_new})
        if product_new == 'new':
            return self.list(category=category, **post)
        if not post.get('dash_number', False):
            return {}
        Product = http.request.env['electron.origin_data'].sudo()
        product_product = http.request.env['product.product'].sudo()
        product_id = product_product.create({'name':post.get('dash_number')})
        post.update({'p_type':category.id,'product_id':product_id.id})
        product_id = Product.create(post)
        url = str(product_id.id)
        return http.request.redirect(url)

    # @http.route([
    #     '/electron/electronic/category/',
    #     '/electron/electronic/category/page/<int:page>',
    #     '/electron/electronic/category/<model("electron.electronic"):category>',
    #     '/electron/electronic/category/<model("electron.electronic"):category>/product/<int:product_id>',
    #     '/electron/electronic/category/<model("electron.electronic"):category>/page/<int:page>',
    #  ], type='http', auth='public', website=True)
    def list(self,  page=0, category=None,  ppg=False, search="", **post):
        category_name = u'基本类'
        search = search.strip()
        disk_rel =http.request.env['electron.disk_center']
        search_data = []
        domain = []
        product_id = post.get('product_id')
        attrib_list = http.request.httprequest.args.getlist('attrib')
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        #content_list2 = http.request.env['electron.content_capacitor'].search([])

        category_id = 0
        ids = post.get("cpo_ids")
        if product_id:
            ids = str(product_id)
        ids = ids if ids != '-1' else None
        ids = [int(re.search("\d*",x).group()) for x in ids.split(",")] if ids else ids
        category_obj_id = post.get('category_obj_id')
        #Product = http.request.env['electron.content']
        Product = http.request.env['electron.origin_data']

        #pager = http.request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        url = '/electron/electronic/category/' + slug(category) if category else ''
        if category_obj_id:
            category = http.request.env['electron.electronic'].search([('id', '=', category_obj_id)])
        if category:
            category_name = category.name
            category_id = category.id
        fields_rel_dict = disk_rel.get_view_disk_rel(type=category_name)
        ids = disk_rel.do_search_origin_data(ids=ids, category=category, search=search)
        domain = [('id', 'in', ids)]
        #if product_id:
            #domain = [('product_id', '=', product_id)]
            #product_row = product_row.search([('id', '=', product_id)])
        product_count = Product.search_count(domain)
        keep = QueryURL(url=url, category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
        pager = http.request.env['website'].pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        content_list = Product.search(domain, limit=ppg, offset=pager['offset'])
        product_row = False
        if product_id:
            product_row = content_list
 #       if category :
 #           #aa=http.request.env['electron.disk_center'].get_ele_data(type_name=None, search=search)

 #           #aa=http.request.env['electron.disk_center'].get_ele_product_ids(type_name=None, search=search)
 #           fields_rel_dict = disk_rel.get_view_disk_rel(type=category.name)
 #           ids = disk_rel.do_search_origin_data(ids=ids, category=category, search=search)
 #           domain = [('id', 'in', ids)]
 #           product_count = Product.search_count(domain)
 #           keep = QueryURL(url=url, category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
 #           pager = http.request.env['website'].pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
 #           #products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
 #           content_list = Product.search(domain, limit=ppg, offset=pager['offset'])
 #           #content_list2 = http.request.env['electron.content_capacitor'].search([('p_type' ,'=', category.id)])
 #           category_id = category.id

 #       else:
 #           #fields_rel_list = self.get_filter_fields(type=base_type)
 #           fields_rel_dict = disk_rel.get_view_disk_rel(type=base_type)
 #           #if not ids and search:
 #           #    fields_rel_list = list(set(fields_rel_list + WEBSITE_SEARCH_FIELDS))
 #           #    domain += [ "|" for x in range(len(fields_rel_list)-1)]
 #           #    domain += [(x, 'ilike', search)for x in fields_rel_list]
 #           #if ids:
 #           #    domain = [("id", 'in', ids)]
 #           ids = disk_rel.do_search_origin_data(ids=ids, category=category, search=search)
 #           domain = [('id', 'in', ids)]
 #           product_count = Product.search_count(domain)
 #           #keep = QueryURL('/electron/electronic/category/', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
 #           keep = QueryURL(url=url, category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
 #           pager = http.request.env['website'].pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
 #           content_list = Product.search(domain, limit=ppg, offset=pager['offset'])

        if not category and content_list:
            category = content_list[0].p_type
            category_id = category.id
            #category_name = category.name
        #if category and category.get_cu_code(category.id) == 'res':
        #    category_id = "temp_1"
        #elif category and category.get_cu_code(category.id) == 'capa':
        #    category_id = "temp_2"
        #else:
        #    category_id = "other"

        return http.request.render('electron.listing', {
            'root': '/electron/electronic',
            'objects': http.request.env['electron.electronic'].search([('parent_id', '=', False)]),
            'get_childs': self.get_childs,
            'content_list': content_list,
            'content_list2': content_list,
            'category_id': category_id,
            'pager': pager,
            'keep': keep,
            'fields_rel_dict':fields_rel_dict,
            #'getattr':lambda obj,x:getattr(obj, x).name if hasattr(getattr(obj, x),'name') else getattr(obj, x),
            'getattr':lambda obj,x:getattr(obj, x),
            'hasattr':lambda obj,x:hasattr(obj, x),
            'get_filter_head':self.get_filter_head,
            'category_obj':category if category else http.request.env['electron.electronic'],
            'cpo_sorted': self.cpo_sorted,
            'search':search,
            'get_type_parent_len': self.get_electron_type_parent_len,
            'product_id': product_row,
            'product_new': True if post.get('product_new') == 'new' else False,
        })

    def get_electron_type_parent_len(self, category_obj):
        p_len = 0
        obj = category_obj
        while obj.parent_id:
            p_len += 1
            obj = obj.parent_id
        return p_len

    def cpo_sorted(self, vals, category_obj, field, get_name=False):
        try:
            category = http.request.env['electron.disk_rel']
            disk_origin =http.request.env['electron.origin_data']
            disk_rel =http.request.env['electron.disk_center']
            fields_rel_dict = disk_rel.get_disk_rel(type=category_obj.name)

            p_type=['基本类',category_obj.name]
            res = category.search([('not_show', '!=', True),('tt_type.name','in',p_type)])
            if len(list(set([x.sequence for x in res]))) == 1:
                res = dict([(getattr(x,field).name if get_name else getattr(x,field),x.id) for x in res])
            else:
                res = dict([(getattr(x,field).name if get_name else getattr(x,field),x.sequence if x.tt_type.code=='base' else x.sequence+100) for x in res])
            vals = sorted(vals, key=lambda x:res.get(x))
        except Exception,e:
            pass
        return vals

    def get_filter_fields(self, type):
        fields = http.request.env['electron.disk_rel'].get_filter_can_fields(type=type)
        return fields

    def get_filter_head(self, type):
        title = http.request.env['electron.disk_rel'].get_filter_can_title(type=type)
        lists = {}
        for row in title:
            items = self.get_filter_items(type=type, title=row)
            lists[row] = items#['Test1','Testxxxxxxxxxxxx']
        return title,lists

    def get_filter_items(self,type,title):
        disk_rel =http.request.env['electron.disk_center']
        disk_origin =http.request.env['electron.origin_data']
        fields_rel_dict = disk_rel.get_view_disk_rel(type=type)
        type_id = http.request.env['electron.electronic'].search([('name', '=', type)]).id
        sup_cr = http.request.env.user.sudo().env.cr
        sup_cr.execute('select distinct {field} from electron_origin_data el_o \
                       join electron_disk_unit_one el_one on el_o.unit_one_id = el_one.id \
                       join electron_base el_b on el_o.base_id = el_b.id and el_b.p_type={p_type};'.format(
                           field=fields_rel_dict.get(title),
                           p_type=type_id
                       ))
        data = map(lambda x:x[0], sup_cr.fetchall())
        return data
        #items = disk_origin.search([('p_type', '=', type)]).mapped(fields_rel_dict.get(title))
        #return list(set(items))

    def get_childs(self,parent_id):
        res = http.request.env['electron.electronic'].search([('parent_id', '=', parent_id.id)])
        return res
