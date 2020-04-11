#-*- coding: utf-8 -*-
from electron_base import Electron_base_item
from odoo import models, fields, api
import re
import logging

WEBSITE_FILTER_NOTCAN_FIELDS= ['dash_number','digi_number']
_logger = logging.getLogger(__name__)
WEBSITE_SEARCH_FIELDS = ['dash_number']

except_list = ['id','create_date','write_date','create_uid','write_uid','__last_update', 'display_name']

#第一个分布式存储单元，用来扩展存储字段
class Electron_disk_unit_one(models.Model):
    _name = 'electron.disk_unit_one'

    #ele_name = fields.One2many('electron.disk_rel',"ele_fileid")  #关联字段
    ele001 = fields.Char()
    ele002 = fields.Char()
    ele003 = fields.Char()
    ele004 = fields.Char()
    ele005 = fields.Char()
    ele006 = fields.Char()
    ele007 = fields.Char()
    ele008 = fields.Char()
    ele009 = fields.Char()
    ele010 = fields.Char()
    ele011 = fields.Char()
    ele012 = fields.Char()
    ele013 = fields.Char()
    ele014 = fields.Char()
    ele015 = fields.Char()
    ele016 = fields.Char()
    ele017 = fields.Char()
    ele018 = fields.Char()
    ele019 = fields.Char()
    ele020 = fields.Char()
    ele021 = fields.Char()
    ele022 = fields.Char()
    ele023 = fields.Char()
    ele024 = fields.Char()
    ele025 = fields.Char()
    ele026 = fields.Char()
    ele027 = fields.Char()
    ele028 = fields.Char()
    ele029 = fields.Char()
    ele030 = fields.Char()

#所有的存储字段库
class Electron_disk_fields(models.Model):
    _name = 'electron.disk_fields'

    name = fields.Char("Name", index=True, copy=False)

    @api.model
    def update_field(self, field):
        assert type(field) == str, 'update_field method update only one recorde.'
        c_ids = self.search([('name','=',field)])
        return c_ids[0] if c_ids else self.create({'name':field})

#管理存储单元字段与类型之间的关系
class Electron_disk_rel(models.Model):
    _name = 'electron.disk_rel'

    sequence = fields.Integer(string='Sequence', default=10, index=True)
    tt_type = fields.Many2one('electron.electronic', string="Type", index=True)     #关联类型
    ele_disk_field_id = fields.Many2one('electron.disk_fields', string="Field id", index=True)   #关联字段
    ele_title = fields.Char(string="Title", translate=True, index=True)                          #标题
    filter_can = fields.Boolean(string="Filter can", index=True)
    not_show =  fields.Boolean(string="not show")

    #获取website可显示字段
    @api.model
    def get_view_title(self, type):
        p_type = []
        p_type.append(type)
        p_type.append('基本类')
        res = self.search([('not_show', '!=', True),('tt_type.name','in',p_type)]).mapped("ele_title")
        return res

    #获取website可搜索字段标题
    @api.model
    def get_filter_can_title(self, type):
        p_type = []
        p_type.append(type)
        p_type.append('基本类')
        res = self.search([
            ('filter_can', '=', True),
            ('tt_type.name','in',p_type),
            ('ele_disk_field_id.name','not in', WEBSITE_FILTER_NOTCAN_FIELDS)]).mapped("ele_title")
        return res

    #获取website可搜索字段名
    @api.model
    def get_filter_can_fields(self, type):
        p_type = []
        p_type.append(type)
        p_type.append('基本类')
        res = self.search([
            ('filter_can', '=', True),
            ('tt_type.name','in',p_type),
            ('ele_disk_field_id.name','not in', WEBSITE_FILTER_NOTCAN_FIELDS)]).mapped("ele_disk_field_id.name")
        return res

    #获取sale get price可搜索字段名
    @api.model
    def get_search_fields_for_sale_price(self, type):
        p_type = []
        p_type.append(type)
        p_type.append('基本类')
        res = self.search([
            ('filter_can', '=', True),
            ('tt_type.name','in',p_type)]).mapped("ele_disk_field_id.name")
        res += self.search([
            ('ele_disk_field_id.name','in',WEBSITE_FILTER_NOTCAN_FIELDS)]).mapped("ele_disk_field_id.name")
        return list(set(res))

    #更新类型与字段的存储关系
    @api.model
    def update_disk_rel(self, vals):
        c_ids = self.search([
            ('tt_type','=',vals.get('tt_type')),
            ('ele_title', '=', vals.get('ele_title'))
            ])
        return c_ids[0] if c_ids else self.create(vals)

    #获取类型与字段的存储关系字典
    '''
        格式如下:
            {'标题':'字段名'}
    '''
    @api.model
    def get_disk_rel(self, tt_type):
        ele_obj = self.env['electron.electronic']
        ele_ids = ele_obj.search([('name', '=', tt_type)], limit=1)
        #if not ele_ids:
        #    return False
        if ele_ids.code != 'base':
            ele_ids += ele_obj.search([('name', '=', '基本类')], limit=1)
        dicts = {}
        for row in ele_ids:
            rows = self.search([('tt_type', '=', row.id)])
            dicts.update(dict([(x.ele_title,x.ele_disk_field_id.name) for x in rows]))
        return dicts

    #获取View类型与字段的存储关系字典
    '''
        格式如下:
            {'标题':'字段名'}
    '''
    @api.model
    def get_view_disk_rel(self, tt_type):
        ele_obj = self.env['electron.electronic']
        ele_ids = ele_obj.search([('name', '=', tt_type)], limit=1)
        #if not ele_ids:
        #    return False
        if ele_ids.code != 'base':
            ele_ids += ele_obj.search([('name', '=', '基本类')])
        dicts = {}
        for row in ele_ids:
            rows = self.search([('tt_type', '=', row.id),('not_show', '!=', True)])
            dicts.update(dict([(x.ele_title,x.ele_disk_field_id.name) for x in rows]))
        return dicts

    #获取存储单元
    @api.model
    def get_unused_field_id(self, tt_type):
        origin_data = self.env['electron.origin_data']
        p_objs = [getattr(origin_data, str(x)) for x in origin_data._inherits.values() if 'unit_' in x]
        all_unit_fields = [x for x in p_objs[0].fields_get_keys() if x not in except_list]
        used_fields = self.search([('tt_type','=',tt_type)]).mapped('ele_disk_field_id').mapped("name")
        return sorted([x for x in all_unit_fields if x not in used_fields and 'ele' in x])

    #使用存储单元
    @api.model
    def to_use_disk_unit(self, vals):
        ele_disk_fields = self.env['electron.disk_fields']
        ele_obj = self.env['electron.electronic']
        ele_ids = ele_obj.search([('name', '=', vals.get('tt_type'))])
        assert vals.get('tt_type'),'not find type string.'
        if vals.get('tt_type') and not ele_ids:
            ele_ids = ele_obj.search([('id','=',ele_obj.add_type(main_type_text="", child_type_text=vals.get("tt_type")).get('child_type'))])
            #return False
        type_obj = ele_ids[0]
        vals.update({'tt_type':type_obj.id})
        unused_fields_list = self.get_unused_field_id(ele_ids[0].id)
        assert unused_fields_list, 'not find unused disk unit field, please call administrator.'
        ele_disk_field_id = ele_disk_fields.update_field(unused_fields_list[:1][0])
        vals.update({'ele_disk_field_id':ele_disk_field_id.id})
        self.update_disk_rel(vals)
        return self.get_disk_rel(type_obj.name)


class Electron_origin_data(Electron_base_item):
    _name = 'electron.origin_data'
    _inherits = {
                'electron.base':'base_id',
                "electron.atta":"atta_id",
                'electron.disk_unit_one':'unit_one_id',
                }

    unit_one_id = fields.Many2one("electron.disk_unit_one", required=True, ondelete='cascade', index=True)
    product_id = fields.Many2one("product.product", "Product", index=True)
    checked = fields.Boolean("Checked")

    #创建原始数据api
    @api.model
    def create_origin_multi_data(self, m_vals, html_id):
        r_ids = []
        try:
            int(html_id)
        except Exception:
            html_id = False
            pass
        if not html_id:
            return False
        html_row = self.env['spider_control.html'].search([('id', '=', int(html_id))])
        for vals in m_vals:
            product_id = self.check_product_recorde(vals)
            vals.update({'product_id':product_id})
            product_obj = self.env['product.product'].browse(product_id)
            if vals.get('price'):
                product_obj.sudo().write({'price': vals.get('price')})
            has_id = self.sudo().search([
                ('dash_number', '=', vals.get('dash_number')),
                ('product_id', '=', vals.get('product_id'))
            ])
            if has_id:
                if len(has_id) > 1:
                    if has_id != has_id.filtered(lambda x:not x.price):
                        has_id.filtered(lambda x:not x.price).unlink()
                    else:
                        has_id.filtered(lambda x:not x.price)[:-1].unlink()
                    has_id = has_id.search([
                        ('dash_number', '=', vals.get('dash_number')),
                        ('product_id', '=', vals.get('product_id'))
                    ])
                    has_id[1:].unlink()
                    has_id = has_id[0:]
                    #has_id = has_id.search([
                        #('dash_number', '=', vals.get('dash_number')),
                        #('product_id', '=', vals.get('product_id'))
                    #])
                    _logger.info("Create electron origin data error 04,find dash_number repeat data: id:{id},dash number:{dash_number}".format(
                        id=has_id.id,
                        dash_number = has_id.dash_number,
                    ))
                    has_id.write(vals)
                    #return has_id.id
            if has_id and not vals.get('price'):
                #return has_id.id
                r_ids.append({'id':has_id.id,'product':has_id.product_id.name})
                continue
            if has_id and vals.get('price'):
                assert len(has_id) == 1, 'error find much dash_number recorde.'
                _logger.info("Create electron origin data error 01,find dash_number repeat data: id:{id},dash number:{dash_number}".format(
                    id=has_id.id,
                    dash_number = has_id.dash_number,
                ))
                has_id.write(vals)
                #return has_id.id#self.search([('id', '=', has_id.id)]).id
                r_ids.append({'id':res.id,'product':res.product_id.name})
                continue
            if vals.get('digi_number'):
                has_row = self.sudo().search([
                    ('digi_number', '=', vals.get('digi_number')),
                ])
                if has_row:
                    assert len(has_row) == 1, 'error find much digi_number recorde.'
                    _logger.info("Create electron origin data error 02,find digi_number repeat data: id:{id},digikey number:{digi_number}".format(
                        id=has_row.id,
                        digi_number = has_row.digi_number,
                    ))
                    has_row.write(vals)
                    #return has_row.id#self.search([('id', '=', has_row.id)])
                    r_ids.append(res.id)
            res = self.create(vals)
            _logger.info("Create electron origin data success, id:{id},dash number:{dash_number}".format(
                id=res.id,
                dash_number = res.dash_number,
            ))
            r_ids.append({'id':res.id,'product':res.product_id.name})
        if html_row.state == 'crawl':
            html_row.write({'state': 'parser'})
        return r_ids

    #创建原始数据api
    @api.model
    def create_origin_data(self, vals):
        product_id = self.check_product_recorde(vals)
        vals.update({'product_id':product_id})
        # same dask_number to update origin_data in has_id not price and vals
        # has price
        product_obj = self.env['product.product'].browse(product_id)
        if vals.get('price'):
            product_obj.sudo().write({'price': vals.get('price')})
        has_id = self.sudo().search([
            ('dash_number', '=', vals.get('dash_number')),
            ('product_id', '=', vals.get('product_id'))
        ])
        if has_id:
            if len(has_id) > 1:
                if has_id != has_id.filtered(lambda x:not x.price):
                    has_id.filtered(lambda x:not x.price).unlink()
                else:
                    has_id.filtered(lambda x:not x.price)[:-1].unlink()
                has_id = has_id.search([
                    ('dash_number', '=', vals.get('dash_number')),
                    ('product_id', '=', vals.get('product_id'))
                ])
                has_id[1:].unlink()
                has_id = has_id[0:]
                #has_id = has_id.search([
                    #('dash_number', '=', vals.get('dash_number')),
                    #('product_id', '=', vals.get('product_id'))
                #])
                _logger.info("Create electron origin data error 04,find dash_number repeat data: id:{id},dash number:{dash_number}".format(
                    id=has_id.id,
                    dash_number = has_id.dash_number,
                ))
                has_id.write(vals)
                return has_id.id
        if has_id and not vals.get('price'):
            return has_id.id
        if has_id and vals.get('price'):
            assert len(has_id) == 1, 'error find much dash_number recorde.'
            _logger.info("Create electron origin data error 01,find dash_number repeat data: id:{id},dash number:{dash_number}".format(
                id=has_id.id,
                dash_number = has_id.dash_number,
            ))
            has_id.write(vals)
            return has_id.id#self.search([('id', '=', has_id.id)]).id
        if vals.get('digi_number'):
            has_row = self.sudo().search([
                ('digi_number', '=', vals.get('digi_number')),
            ])
            if has_row:
                assert len(has_row) == 1, 'error find much digi_number recorde.'
                _logger.info("Create electron origin data error 02,find digi_number repeat data: id:{id},digikey number:{digi_number}".format(
                    id=has_row.id,
                    digi_number = has_row.digi_number,
                ))
                has_row.write(vals)
                return has_row.id#self.search([('id', '=', has_row.id)])
        res = self.create(vals)
        _logger.info("Create electron origin data success, id:{id},digikey number:{digi_number}".format(
            id=res.id,
            digi_number = res.digi_number,
        ))
        return res.id

    @api.model
    def update_dash_number(self, vals):
        return vals.replace("\'","\'\'")
    '''
        检查产品是否存在：
            存在则进行匹配变体属性：
                用有不同再创建变体
                否则返回存在的记录对象
    '''
    @api.model
    def check_product_recorde(self, vals):
        #product_record = self.product_id.search([('name', '=', vals.get('dash_number'))])
        domain = '''
            select p.id from product_template t join \
            product_product p on t.name = '{dash_number}' and p.product_tmpl_id = t.id;\
            '''.format(dash_number=self.update_dash_number(vals.get('dash_number')))
        product_ids = self.env.cr.execute(domain)
        product_ids = self.env.cr.fetchall()
        product_ids = [x[0] for x in product_ids if x]
        product_record = self.product_id.browse(product_ids)
        #if not product_record:
            #product_record = self.create_product_id(vals)
        return self.check_product_attribute(product_record if product_record else product_record, vals)

    #检查产品变体的属性值，不存在就创建并关联到产品
    @api.model
    def check_product_attribute(self, records, vals):
        record = False
        for record in records:
            attr_ids = []
            if 'mini_quantity' in vals.keys():
                mini_number = re.search("\d*",vals.get('mini_quantity'))
                if mini_number:
                    mini_number = mini_number.group(0)
                    get_attr = self.get_product_attribute('mini_number', mini_number)
                    self.env.cr.execute('''
                        select rel.product_product_id id \
                            from product_attribute_value_product_product_rel rel \
                                        where rel.product_attribute_value_id = {attri_id} \
                                            and rel.product_product_id != {product_id}
                                        '''.format(attri_id = get_attr.id, product_id = record.id))
                    product_ids = self.env.cr.fetchall()
                    #product_ids = [x[0] for x in product_ids if x]
                    #if get_attr and record not in get_attr.product_ids:
                    #if get_attr and record.id not in product_ids:
                    if get_attr and product_ids:
                        attr_ids.append(get_attr)
            if 'packaging' in vals.keys():
                package = vals.get('packaging')
                if package:
                    #package = self.update_product_attribute('package', package)
                    get_attr = self.get_product_attribute('package', package)
                    self.env.cr.execute('''
                        select rel.product_product_id id \
                            from product_attribute_value_product_product_rel rel \
                                        where rel.product_attribute_value_id = {attri_id} \
                                            and rel.product_product_id != {product_id}
                                        '''.format(attri_id = get_attr.id, product_id = record.id))
                    product_ids = self.env.cr.fetchall()
                    #product_ids = [x[0] for x in product_ids if x]
                    #if get_attr and record not in get_attr.product_ids:
                    #if get_attr and record.id not in product_ids:
                    if get_attr and product_ids:
                        attr_ids.append(get_attr)
            check_old_has = set([x.name for x in attr_ids]) - set([vals.get('mini_quantity'), vals.get('packaging')] + ["", '-'])
            if check_old_has:
                break
                    #get_attr.write({'product_ids':[(4,record.id)]})
        #product_tmp_ids = self.env['product.template'].search([('name', '=', vals.get('dash_number'))])
        #if not record and product_tmp_ids:
            #product_tmp_id = product_tmp_ids[0].id
        #else:
            #product_tmp_id = record.product_tmpl_id.id
        if not record:
            record = records
            product_tmp_id = record.product_tmpl_id.id
            record=self.create_product_id(vals, product_tmpl_id=product_tmp_id)
            if 'mini_quantity' in vals.keys():
                mini_number = re.search("\d*",vals.get('mini_quantity'))
                if mini_number and mini_number.group(0):
                    mini_number = mini_number.group(0)
                    get_attr = self.get_product_attribute('mini_number', mini_number)
                    record.write({'attribute_value_ids':[(4,get_attr.id)]})
            if 'packaging' in vals.keys():
                package = vals.get('packaging')
                if package:
                    #package = self.update_product_attribute('package', package)
                    get_attr = self.get_product_attribute('package', package)
                    record.write({'attribute_value_ids':[(4,get_attr.id)]})
            #for attr_id in attr_ids:
            #    record.write({'attribute_value_ids':[(4,attr_id)]})
        return record.id

    #检查变休属性，没有就创建
    @api.model
    def get_product_attribute(self, key, value):
        product_attr = self.env['product.attribute']
        product_attr_val = self.env['product.attribute.value']
        #mini_number_obj = self.env.ref("electron.product_attribute_mini_number")
        #package_obj = self.env.ref("electron.product_attribute_package")
        attr_id = product_attr.search([('name','=',key)], limit=1)
        if not attr_id:
            attr_id = product_attr.create({'name':key})
        p_ids = product_attr_val.search([
            ('attribute_id','=', attr_id.id),
            ('name','=',value)
        ])
        if p_ids:
            return p_ids
        return product_attr_val.create({
            'attribute_id': attr_id.id,
            'name': value,
        })

    @api.multi
    def update_digi_number_only_one(self):
        list = self.search([('digi_number', '!=', False),('checked', '=', False)], limit=1000).mapped("id")
        #for r_id in list:
        while(list):
            r_id = list.pop(-1) if list else False
            row = self.search([('id', '=', r_id)])
            if not row:
                continue
            row.search([('digi_number', '=', row.digi_number),('id','!=', row.id)]).unlink()
            row.checked = True
            if not list:
                self.env.cr.commit()
                list = self.search([('digi_number', '!=', False),('checked', '=', False)], limit=1000).mapped("id")
                #r_id = list.pop(-1) if list else False

    #创建产品的接口
    @api.model
    def create_product_id(self, vals, product_tmpl_id=None):
        product_category = self.env['product.category']
        product_category_id = self.env.ref('electron.product_category_electronic_material')
        price = '0'
        if 'price' in vals.keys():
            try:
                price = vals.get('price').split(u'\xa5')[1] if u'\xa5' in vals.get('price') else vals.get('price')
                price = vals.get('price').split('$')[1] if '$' in vals.get('price') else vals.get('price')
                price = price.replace(" ","").replace(",","")
                price = float(price)
            except Exception,e:
                pass
        new_vals = {
            'name':vals.get('dash_number'),
            'categ_id': product_category_id.id,
            'price': price,
            'type': 'product',
            #'image_medium': vals.get('cpo_image'),
        }
        if vals.get('encapsulation'):
            ele_encapsulation = self.env['cpo.electron.encapsulation']
            encap_row = ele_encapsulation.update_encapsulation(vals.get('encapsulation'))
            new_vals.update({'encapsulation': encap_row.id})
        if product_tmpl_id:
            new_vals.update({'product_tmpl_id':product_tmpl_id})
        else:
            old_tmp_sql = '''
                select id from product_template where name='{}';
                '''.format(self.update_dash_number(vals.get('dash_number')))
            self.env.cr.execute(old_tmp_sql)
            templ_old = self.env.cr.fetchone()
            if templ_old:
                new_vals.update({'product_tmpl_id':templ_old[0]})
                _logger.info("Hit old product_template id:{},dash_number:{}".format(templ_old[0],vals.get('dash_number')))
        product_id = self.with_context({'lang':'en_US'}).env['product.product'].create(new_vals)
        return product_id

#存储关系中心，用来测试分布式存储系统
class Electron_disk_center(models.Model):
    _name = 'electron.disk_center'

    name = fields.Char("Name")
    p_type = fields.Char("Type")
    title = fields.Char("Title")
    result = fields.Char("Reslut")

    #初使化基本字段库的存储关系数据
    @api.model
    def add_init_fields_rel(self, context=None):
        p_type='基本类'
        #origin_data = self.env['electron.origin_data'].with_context({'lang':'en_US'})
        origin_data = self.env['electron.origin_data'].with_context({'lang':'zn_CN'})
        ele_disk_rel = self.env['electron.disk_rel']
        disk_fields = self.env['electron.disk_fields']
        ele_type = self.env['electron.electronic']
        type_obj = ele_type.search([('name','=',p_type)])
        p_objs = [getattr(origin_data, str(x)) for x in origin_data._inherits.values() if 'unit_' not in x]
        field_string_dict = {}
        for row in p_objs:
            field_string_dict.update(dict([(x[0],x[1].get('string')) for x in row.fields_get().items() if x[0] not in except_list]))
        field_ids_rel = dict([(x,disk_fields.update_field(x)) for x in field_string_dict.keys()])
        cn_field_string_dict = self.env['ir.translation'].get_field_string('electron.base')
        cn_field_string_dict.update(self.env['ir.translation'].get_field_string('electron.atta'))
        cn_field_string_dict = dict([x for x in cn_field_string_dict.items() if x[0] not in except_list])
        for row in field_string_dict.keys():
            ele_disk_rel.update_disk_rel({
                'tt_type':type_obj.id,
                'ele_disk_field_id':field_ids_rel.get(row).id,
                #'ele_title': field_string_dict.get(row)
                'ele_title': cn_field_string_dict.get(row)
            })
        return True

    #获取存储关系数据
    @api.multi
    def get_disk_rel_api(self,
                        context=None,
                        type=None,
                        dash_number=None,
                        cpo_image=None,
                        price=None,
                        encapsulation=None,
                        mini_quantity=None,
                        packaging=None,
                        description=None,
                        series=None,
                        manufacture=None,
                        digi_number=None,
                        mini_image_herf=None,
                        big_image_herf=None,
                        ):
        '''
        指定固定字段的关联:
            dash_number -->制造商零件编号
            cpo_image -->图像
            price -->单价
            encapsulation  -->封装/外壳
            mini_quantity  -->最低订购数量是
            packaging  -->包装
            description     #描述
            series    #系列
            manufacture       #制造商
            digi_number     #digikey number
            mini_image_herf     #小图像链接
            big_image_herf      #大图像链接
        '''
        res = self.get_disk_rel(context=context, type=type)
        if not res:
            self.add_init_fields_rel(context=context)
            res = self.get_disk_rel(context=context, type=type)
        #lang = self.env.user.lang
        #lang = 'en_US'
        lang = 'zh_CN'
        if dash_number:
            res.update({
                dash_number: res.get(u'制造商零件编号') if lang == 'zh_CN' else res.get('Manufacturer P/N'),
            })
        if cpo_image:
            res.update({
                cpo_image: res.get(u'图像') if lang == 'zh_CN' else res.get('Image'),
            })
        if price:
            res.update({
                price: res.get(u'单价','价格') if lang == 'zh_CN' else res.get('Price'),
            })
        if encapsulation:
            res.update({
                encapsulation: res.get(u'封装/外壳') if lang == 'zh_CN' else res.get('Encapsulation'),
            })
        if mini_quantity:
            res.update({
                mini_quantity: res.get(u'最低订购数量是', u'最低订购数量') if lang == 'zh_CN' else res.get('Minimum Order Quantity'),
            })
        if packaging:
            res.update({
                packaging: res.get(u'包装') if lang == 'zh_CN' else res.get('Packaging'),
            })
        if description:
            res.update({
                description: res.get(u'描述') if lang == 'zh_CN' else res.get('Description'),
            })
        if series:
            res.update({
                series: res.get(u'系列') if lang == 'zh_CN' else res.get('Series'),
            })
        if manufacture:
            res.update({
                manufacture: res.get(u'制造商') if lang == 'zh_CN' else res.get('Manufacturer'),
            })
        if digi_number:
            res.update({
                digi_number: res.get(u'得捷电子零件编号') if lang == 'zh_CN' else res.get('Digikey P/N'),
            })
            res.update({
                digi_number: res.get(u'Digi-Key 零件编号') if lang == 'zh_CN' else res.get('Digikey P/N'),
            })
        if mini_image_herf:
            res.update({
                mini_image_herf: res.get(u'小图像链接') if lang == 'zh_CN' else res.get('Mini Image Herf'),
            })
        if big_image_herf:
            res.update({
                big_image_herf: res.get(u'大图像链接') if lang == 'zh_CN' else res.get('Big Image Herf'),
            })
        return res

    #获取存储关系数据
    @api.multi
    def get_disk_rel(self, context=None, type=None):
        ele_disk_rel = self.env['electron.disk_rel']
        return ele_disk_rel.get_disk_rel(type)

    @api.multi
    def button_get_disk_rel(self, context=None):
        self.result = self.get_disk_rel(context=context, type=self.p_type)

    #获取存储关系数据，如果没有就创建
    @api.multi
    def to_use_disk_rel(self, context=None, type=None, title=None):
        ele_disk_rel = self.env['electron.disk_rel']
        return ele_disk_rel.to_use_disk_unit({
            'tt_type':type,
            'ele_title':title,
            })

    @api.multi
    def button_to_use_disk_rel(self, context=None):
        self.result = self.to_use_disk_rel(context=context, type=self.p_type, title=self.title)

    #获取View存储关系数据
    @api.multi
    def get_view_disk_rel(self, context=None, type=None):
        ele_disk_rel = self.env['electron.disk_rel']
        return ele_disk_rel.get_view_disk_rel(type)

    #获取base字段列表
    @api.multi
    def from_field_get_table_name(self, context=None, field=None):
        ele_disk_rel = self.env['electron.base']
        unit_one = self.env['electron.disk_unit_one']
        if field in ele_disk_rel.fields_get_keys():
            return 'electron_base'
        if field in unit_one.fields_get_keys():
            return 'electron_disk_unit_one'
        return False

    #执行sql
    @api.model
    def do_execute(self, context=None, sql=None):
        su_self = self.env.user.sudo().env
        su_self.cr.execute(sql)
        res = su_self.cr.fetchall()
        return [x[0] for x in res if x] if res else []

    @api.multi
    def button__view_get_disk_rel(self, context=None):
        self.result = self.get_view_disk_rel(context=context, type=self.p_type)

    '''
    获取电子物料数据
    参数:
        search  --> 搜索值
    '''
    @api.model
    def get_ele_data(self, type_name = None, search=None):
        ele_data = self.env['electron.origin_data']
        #domain_fields = ['dash_number', 'digi_number']
        domain_fields = ['dash_number']
        domain = []
        domain += ["|" for x in range(len(domain_fields)-1)]
        domain += [(x, 'ilike', search) for x in domain_fields]
        res_ids = ele_data.search(domain)
        return res_ids
    #@api.model
    #def get_ele_data(self, type_name = None, search=None):
    #    res_ids = []
    #    type_obj = self.env['electron.electronic']
    #    ele_data = self.env['electron.origin_data']
    #    if not type_name:
    #        type_list = type_obj.search([])
    #    else:
    #        type_list = type_obj.search([('name', '=', type_name)])
    #    for category in type_list:
    #        type_name = category.name
    #        assert category,'Type name {n} is not exist.'.format(n=type_name)
    #        fields_rel_list = self.env['electron.disk_rel'].get_search_fields_for_sale_price(type=type_name)
    #        domain = [('p_type', '=', category.id)]
    #        if search and fields_rel_list:
    #            domain += [ "|" for x in range(len(fields_rel_list)-1)]
    #            domain += [(x, 'ilike', search)for x in fields_rel_list]
    #        if ele_data.search(domain):
    #            res_ids.append(ele_data.search(domain))
    #    return res_ids

    '''
    获取产品id
    '''
    @api.model
    def get_ele_product_ids(self, type_name = None, search=None):
        res_ids = self.get_ele_data(type_name=type_name, search=search)
        datas = []
        for row in res_ids:
            datas += [x for x in row.filtered(lambda x:x.product_id).mapped("product_id") if x]
        return datas

    '''
    从产品对象获取电子物料数据
    参数:
        search  --> 搜索值
    '''
    @api.model
    def get_product_price(self, search=None):
        #product_pool = self.env['product.product']
        #domain = [('name', '=', search), ('price', '>', 0)]
        #res_ids = product_pool.search(domain, limit=1)
        domain = ""
        for row in search.split(" "):
            domain += " or {table_name}.name ilike '{name}'".format(table_name="tmp",name=row)
        sql_code = '''
                select tmp.list_price,enp.name,tmp.name from product_template tmp\
                    join cpo_electron_encapsulation enp \
                    on ({domain}) and tmp.list_price > 0 and tmp.encapsulation = enp.id;
                '''.format(domain=domain[4:])
        sql_code_single = '''
               select tmp.list_price,enp.name,tmp.name from product_template tmp\
                   join cpo_electron_encapsulation enp \
                   on tmp.name='{name}' and tmp.list_price > 0 and tmp.encapsulation = enp.id;
        '''.format(name=str(search))
        self.env.cr.execute(sql_code_single)
        p_price = self.env.cr.fetchone()
        if p_price and not p_price[2]:
            self.env.cr.execute(sql_code)
            p_price = self.env.cr.fetchone()
        return {
            'price':p_price[0] if p_price else 0,
            'package': p_price[1] if p_price else '',
            'name': p_price[2] if p_price else '',
        }

    '''
    Check repeat Product
    '''
    @api.multi
    def check_repeat_product(self):
        product_pool = self.env['product.product']
        i = 0
        _logger.info("Check repeat Product log:Starting.")
        while True:
            has_ids = product_pool.search([('checked_repeat', '=', False)], limit=5000, order='id desc')
            if not has_ids or i >= 5000:
                break
            #for row in has_ids:
            row = has_ids[0]
            ref_list = [(x.attribute_id.name,x.name) for x in row.attribute_value_ids]
            repeat_ids = product_pool.search([('product_tmpl_id', '=', row.product_tmpl_id.id),('id', '!=', row.id),('checked_repeat', '=', False)])
            for x1 in [x for x in repeat_ids if [(y.attribute_id.name,y.name) for y in x.attribute_value_ids] == ref_list]:
                _logger.info("Check repeat Product log:unlink product_id:{product_id},dash_number:{dash_number}, number:{number}".format(product_id=x1.id,dash_number=x1.name, number=i))
                x1.unlink()
                break
            row.checked_repeat = True
            if i % 50 == 1:
                self.env.cr.commit()
                _logger.info("Check repeat Product log:cr to commit.")
            i+=1
        _logger.info("Check repeat Product log:End.")

    def get_filter_fields(self, type):
        fields = self.env['electron.disk_rel'].get_filter_can_fields(type=type)
        return fields

    '''
    搜索原始数据
    '''
    @api.model
    def do_search_origin_data(self, ids=None, category=None, search=None):
        domain2 = ""
        fields_rel_list = []
        condition = ''
        base_type = u'基本类'
        if not category and search:
            fields_rel_list = self.get_filter_fields(base_type)
        elif category:
            condition = 'and'
            domain2 = 'electron_electronic.id = {cat_id}'.format(cat_id=category.id)
            fields_rel_list = self.get_filter_fields(type=category.name)
        else:
            condition = 'and'
            domain2 = 'electron_base.id = 0'
        fields_rel_list = list(set(fields_rel_list + WEBSITE_SEARCH_FIELDS))
        if not ids and search:
            domain_x = "CONCAT("
            for search_sub in search.split():
                if fields_rel_list and len(search.split()) > 1:
                    domain_x += ' and ('
                check_i = False
                for x in fields_rel_list:
                    table_name=self.from_field_get_table_name(field=x)
                    if not table_name:
                        continue
                    #domain_x += "{check_or}{table}.{field_x} ilike '%{search}%'".format(check_or=' or ' if check_i else '',table=table_name,field_x=x,search=search_sub.encode('utf-8'))
                    domain_x += "{check_or}{table}.{field_x} ".format(check_or=' , ' if check_i else '',table=table_name,field_x=x,search=search_sub.encode('utf-8'))
                    check_i = True
                domain_x += ") ilike '%{search}%'".format(search=search_sub.encode('utf-8'))
                if fields_rel_list and len(search.split()) > 1:
                    domain_x += ')'
            if len(search.split()) > 1:
                domain_x = domain_x[5:]
            domain2 += " {condition} ({do})".format(condition=condition,do=domain_x) if domain_x else ""
        if ids:
            domain = [("id", 'in', ids)]
            if len(ids) == 1:
                domain2 = 'o.id = {ids}'.format(ids = ids[0])
            else:
                domain2 = 'o.id in {ids}'.format(ids = tuple(ids))

        sql_sel = '''
            select o.id from electron_base\
                join electron_electronic on electron_electronic.id = electron_base.p_type \
                join electron_origin_data o on o.base_id = electron_base.id \
                join electron_disk_unit_one on {domain} {condition} electron_disk_unit_one.id = o.unit_one_id;\
        '''.format(condition='and' if domain2 else '',domain=domain2)
        ids = self.do_execute(sql=sql_sel)
        return ids

    #获取价格为零的digikey 编号 ele_len为取的长度
    @api.model
    def get_zero_price_for_digi_number(self, ele_len=1):
        origin_data = self.env['electron.origin_data']
        origin_ids = origin_data.sudo().search([('price', '=', '')], limit=ele_len)
        return origin_ids.mapped("digi_number")

    #更新digikey 编号对应的单价
    @api.model
    def update_price_for_digi_number(self, digi_number, price):
        if not price:
            return 'error:price is null'
        try:
            float(price)
        except Exception,e:
            return 'error:Please check price format,must float and string'
        origin_data = self.env['electron.origin_data']
        origin_id = origin_data.sudo().search([('digi_number', '=', digi_number)], limit=1)
        if not origin_id:
            return 'error:not find digi_number:{}'.format(digi_number)
        if float(price):
            origin_id.write({'price': str(price)})
            origin_id.product_id.sudo().write({'price': float(price)})
        else:
            origin_id.write({'price': '0.0'})
        return True

