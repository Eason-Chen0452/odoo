# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class CpoOfferBomDataWizard(models.TransientModel):
    _name = 'cpo_offer_bom.cpo_multi_ele_wizard'

    cpo_ele_wizard_line = fields.One2many('cpo_offer_bom.cpo_multi_ele_wizard_line', 'cpo_ele_wizard', string="Search Reasult")
    # cpo_search_bom_result = fields.Many2one('cpo_offer_bom.wizard', string="cpo_wizard", ondelete="cascade")



    @api.model
    def default_get(self, fields_list):
        res = super(CpoOfferBomDataWizard, self).default_get(fields_list)
        if self.env.context.get('active_model') == 'cpo_offer_bom.bom_line':
            bom_obj = self.env['cpo_offer_bom.bom_line']
            bom_id = self.env.context.get('active_id')
            bom_row = bom_obj.search([('id', '=', bom_id)])
            description = bom_row.cpo_description
            mfr_p_n = bom_row.cpo_mfr_p_n
            remark = bom_row.cpo_remark
            vals = []
            disk_rel = self.env['electron.disk_center']
            origin_obj = self.env['electron.origin_data']
            if mfr_p_n:
                product_ids = disk_rel.get_product_price(search=mfr_p_n)
                #search_line_result = disk_rel.do_search_origin_data(search=mfr_p_n)
                #orgin_ids = origin_obj.search([('id', 'in', search_line_result)], limit=30)
                if product_ids.get('name'):
                #for row in orgin_ids:
                    vals.append((0,0, {
                        'cpo_manuf_pn':product_ids.get('name'),
                        'cpo_price': product_ids.get('price'),
                        'cpo_package': product_ids.get('package'),
                    }))
            if not vals and (description or remark):
                search = description if description else remark
                search_line_result = disk_rel.do_search_origin_data(search=search)
                orgin_ids = origin_obj.search([('id', 'in', search_line_result)], limit=30)
                for row in orgin_ids:
                    vals.append((0,0, {
                        'cpo_manuf_pn':row.dash_number,
                        'cpo_price': float(row.price),
                        'cpo_package': row.encapsulation,
                    }))
                #res.update({'cpo_ele_wizard_line': vals})
            if vals:
                res.update({'cpo_ele_wizard_line': vals})

            #bom_ref = {}
            #for row in bom_fields_pool:
                #bom_ref.update({row.src_title: row.cpo_title})
        return res

    @api.multi
    def confirm_electron_p_n(self):
        res = []
        bom_obj = self.env['cpo_offer_bom.bom_line']
        bom_id = self.env.context.get('active_id')
        bom_row = bom_obj.search([('id', '=', bom_id)])
        cu_ele = [x for x in self.cpo_ele_wizard_line if x.cpo_confirm]
        if not cu_ele:
            raise ValidationError(_("Please Choice record more then zero!"))
        if cu_ele:
            #bom_row.cpo_mfr_p_n = cu_ele[0].cpo_manuf_pn
            if bom_row.cpo_mfr_p_n != cu_ele[0].cpo_manuf_pn:
                bom_row.cpo_replace_p_n = cu_ele[0].cpo_manuf_pn
            bom_row.cpo_package = cu_ele[0].cpo_package
            bom_row.price = cu_ele[0].cpo_price
            bom_row.total = bom_row.price * bom_row.cpo_qty
            bom_row.base_table_bom_id.to_calc_total()
        return True

    ##select bom
    #@api.multi
    #def cpo_select_bom(self):

        #select_id = self.cpo_bom_line_id
        #temp_bom_line = self.env['cpo_offer_bom.bom_line'].search([('id', '=', select_id)])
        #temp_bom_line.write({
            #"cpo_mfr": self.cpo_manuf,
            #"cpo_mfr_p_n": self.cpo_manuf_pn,
            #"price": self.cpo_price,
            #"cpo_description": self.cpo_bom_descriprion
        #})

        #sql_sel = '''
                    #select o.id from electron_base\
                        #join electron_electronic on electron_electronic.id = electron_base.p_type \
                        #join electron_origin_data o on o.base_id = electron_base.id \
                        #join electron_disk_unit_one on {domain} {condition} electron_disk_unit_one.id = o.unit_one_id;\
                #'''

class CpoOfferBomDataWizard_line(models.TransientModel):
    _name = 'cpo_offer_bom.cpo_multi_ele_wizard_line'

    cpo_ele_wizard = fields.Many2one('cpo_offer_bom.cpo_multi_ele_wizard', string="cpo multi ele", ondelete="cascade")
    cpo_manuf = fields.Char(string="Manufacturer")
    cpo_bom_line_id = fields.Char(string="Bom Line ID")
    cpo_manuf_pn = fields.Char(string="Manufacturer P/N")
    #cpo_price = fields.Char(string="Price", ondelete="cascade")
    cpo_price = fields.Float(string="Price")
    cpo_bom_descriprion = fields.Char(string="Description")
    cpo_confirm = fields.Boolean("Choice Electron")
    cpo_package = fields.Char(string="Package")
