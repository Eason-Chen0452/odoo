#-*- coding: utf-8 -*-
from electron_base import Electron_base_item
from odoo import models, fields, api

from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    encapsulation = fields.Many2one("cpo.electron.encapsulation","Encapsulation")
    level_price_line = fields.One2many("cpo.product.level.price", 'product_template_id', 'Level Price Line')

class ProductProduct(models.Model):
    _inherit = "product.product"

    checked_repeat = fields.Boolean("Checked Repeat")

    @api.multi
    def unlink(self):
        res = super(ProductProduct, self).unlink()
        return res

    '''
    API:
        Update product Level Price Line
        fun name: cpo_update_level_price
        args: dash_number, min_number , price
        return True is success
    '''
    @api.model
    def cpo_update_level_price(self, dash_number, min_number, price):
        try:
            price = float(price)
            min_number = int(min_number)
            dash_number = str(dash_number)
        except Exception:
            return 'Format Error:dash_number:{},min_number:{},price:{}'.format(dash_number, min_number, price)
        sql = '''
            select p.id from product_template t join product_product p on  t.name='{dash_number}' and p.product_tmpl_id = t.id;
        '''.format(dash_number=dash_number)
        self.env.cr.execute(sql)
        has_ids = self.env.cr.fetchall()
        has_dash = self.browse([x[0] for x in has_ids])
        if len(has_dash) >= 1:
            if len(has_dash) > 1:
                has_dash[:-1].unlink()
                self.env.cr.execute(sql)
                has_ids = self.env.cr.fetchall()
            has_dash = self.browse([x[0] for x in has_ids])
            res = has_dash._to_update_level_price(min_number, price)
        else:
            new_dash = self.to_create_new_electron_product(dash_number, price)
            res = new_dash._to_update_level_price(min_number, price)
        if res:
            return 'Update Success!'
        else:
            return 'Update Fault!'

    @api.model
    def to_create_new_electron_product(self, dash_number, price):
        product_category_id = self.env.ref('electron.product_category_electronic_material')
        return self.create({
            'name': dash_number,
            'categ_id': product_category_id.id,
            'price': price,
            'type': 'product',
        })

    @api.multi
    def _to_update_level_price(self, min_number, price):
        return self.level_price_line._to_update_level(self.product_tmpl_id.id, min_number, price)

class ProductLevelPrice(models.Model):
    _name = 'cpo.product.level.price'
    _order = 'cpo_min_number'

    cpo_min_number = fields.Integer("Min Number")
    cpo_price = fields.Float("Price")
    product_template_id = fields.Many2one("product.template", 'Product Template', index=True)

    @api.multi
    def _to_update_level(self, product_tmpl_id, min_number, price):
        base_domin = [('id', 'in', self.ids)]
        self.search(base_domin + [('cpo_min_number', '<=', min_number), ('cpo_price', '<=', price)]).unlink()
        self.search(base_domin + [('cpo_min_number', '>=', min_number), ('cpo_price', '>=', price)]).unlink()
        #if self.search_count(base_domin + [('cpo_min_number', '=', 1)]) == 0:
            #self.create({
                #'product_template_id': product_tmpl_id,
                #'cpo_min_number': 1,
                #'cpo_price': price
            #})
        #else:
        self.create({
            'product_template_id': product_tmpl_id,
            'cpo_min_number': min_number,
            'cpo_price': price
        })
        return True

    @api.constrains("cpo_min_number", 'cpo_price')
    def _check_number_and_cpo_price(self):
        ret_error = ""
        #check min_number avaiable
        if self.cpo_min_number <= 0:
            ret_error += _("Min Number must more than 1;\n")

        #check cpo_price avaiable
        if self.cpo_price <= 0:
            ret_error += _("Price must more than 1;\n")

        #check cpo_min_number repeat
        ch_domain = [
            ('product_template_id', '!=', False),
            ('product_template_id', '=', self.product_template_id.id),
            ('cpo_min_number', '=', self.cpo_min_number),
            ('id', '!=', self.id)
        ]
        if self.search_count(ch_domain) > 0:
            ret_error += _('Find Min_number:{min_number} repeat;\n'.format(
                min_number=self.cpo_min_number
            ))

        #check cpo_min_number and price level avaiable
        ch_domain = [
            ('product_template_id', '!=', False),
            ('product_template_id', '=', self.product_template_id.id),
            ('cpo_min_number', '>=', self.cpo_min_number),
            ('cpo_price', '>=', self.cpo_price),
            ('id', '!=', self.id)
        ]
        ch_domain2 = [
            ('product_template_id', '!=', False),
            ('product_template_id', '=', self.product_template_id.id),
            ('cpo_min_number', '<=', self.cpo_min_number),
            ('cpo_price', '<=', self.cpo_price),
            ('id', '!=', self.id)
        ]
        if  self.search_count(ch_domain) > 0:
            check_cpo = self.search(ch_domain)
            ret_error += _('Find Level Price Not Avaiable:\n\
                           old:{dash_number} : {min_number} : {price} ;\n\
                           new:{dash_number_new} : {min_number_new} : {price_new} ;\n'.format(
                dash_number = check_cpo.product_template_id.name,
                min_number = check_cpo.cpo_min_number,
                price = check_cpo.cpo_price,
                dash_number_new = self.product_template_id.name,
                min_number_new = self.cpo_min_number,
                price_new = self.cpo_price,
            ))
        if  self.search_count(ch_domain2) > 0:
            check_cpo = self.search(ch_domain2)
            ret_error += _('Find Level Price Not Avaiable:\n\
                           old:{dash_number} : {min_number} : {price} ;\n\
                           new:{dash_number_new} : {min_number_new} : {price_new} ;\n'.format(
                dash_number = check_cpo.product_template_id.name,
                min_number = check_cpo.cpo_min_number,
                price = check_cpo.cpo_price,
                dash_number_new = self.product_template_id.name,
                min_number_new = self.cpo_min_number,
                price_new = self.cpo_price,
            ))

        #return error to
        if ret_error:
            raise ValidationError(_("Chack Level Error:\n{ret_error}").format(
                ret_error = ret_error
            ))


class cpo_electron_encapsulation(models.Model):
    _name = "cpo.electron.encapsulation"

    name = fields.Char("Name", index=True)
    pin_number = fields.Integer("Pin Number")

    @api.constrains('name')
    def check_encapsulation(self):
        number = self.search([('name', '=', self.name)])
        if len(number)>1:
            raise ValidationError(_("Chack electron encapsulation error, Current encapsulation already exists!"))

    @api.model
    def update_encapsulation(self, values):
        assert values, 'update encapsulation error, values is null.'
        assert type(values) in (str,unicode), 'update encapsulation error, values type not is string.'
        has_ids = self.search([('name','=',values)])
        return has_ids[0] if has_ids else self.create({'name':values})
