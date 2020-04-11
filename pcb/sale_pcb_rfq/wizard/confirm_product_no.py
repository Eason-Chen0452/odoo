# -*- coding: utf-8 -*-


from odoo import api, fields, models, _, tools
from odoo.osv import osv


class confirm_product_no(osv.osv_memory):
    _name = 'confirm.product.no'
    _description = 'Confirm Product No'

    def _get_pcb_delivery_time(self):
        vals = 22.0
        if self.env.context.get('active_model') == 'sale.quotation':
            row = self.pool.get('sale.quotation').browse(self.env.context.get('active_id'))
            vals = row.partner_id.pcb_delivery_time or vals
        return vals

    confirm_line = fields.One2many('confirm.product.no.line', 'confirm_id', 'Quotation Lines')
    new_partner = fields.Boolean('New Partner')
    pcb_partner_delivery_time = fields.Float('PCB Partner Delivery Time',digits=(12,4))

    _defaults = {
        'pcb_partner_delivery_time':_get_pcb_delivery_time,
    }

    def default_get(self, fields):
        """
        Default get for name, opportunity_ids.
        If there is an exisitng partner link to the lead, find all existing
        opportunities links with this partner to merge all information together
        """
        res = super(confirm_product_no, self).default_get(fields)
        quo_obj = self.pool.get('sale.quotation')
        res_id = self.env.context.get('active_id')
        quo_res = quo_obj.browse(res_id)
        if not quo_res.quotation_line:
            raise osv.except_osv(_('Quotation Line Error!'), _('Please enter at least one line of Quotation Line!'))
        value = []
        for row in quo_res.quotation_line:
            product_no = row.product_no and row.product_no or '/'
            value.append((0,0,{'product_no': product_no,'customer_file_name':row.customer_file_name}))
        res.update({'confirm_line' : value})
        return res

    def confirm_product_no(self):
        import re
        quo_pool = self.pool.get('sale.quotation')
        quo_line_pool = self.pool.get('sale.quotation.line')
        quo_id = self.env.context.get('active_id')
        rows = self.browse(self.env.ids[0])
        self.env.context['remember_reorder_sale'] = {}
        for row in rows.confirm_line:
            if not row.product_no:
                raise osv.except_osv(_('Quotation Null Error!'), _('Please enter Product No!'))
            elif not re.match('^[A-Z /]+$',row.product_no[len(row.product_no)-1:]):
                raise osv.except_osv(_('Quotation Product No Error!'), _('Product No Must is A-Z!'))
            quo_l_rows = quo_line_pool.search([('quotation_id','=',quo_id),('customer_file_name','=',row.customer_file_name)])
            if len(quo_l_rows) >1:
                raise osv.except_osv(_('Customer File Name Error!'), _('Find the same file name!'))
            #quo_l_rows = quo_line_pool.browse(cr, uid, quo_l_rows, context=context)   
            #context['quo_id'] = quo_l_rows[0]
            quo_line_pool.write(quo_l_rows[0], {'product_no':row.product_no})
            if row.product_no and row.product_no != '/':
                self.env.context['remember_reorder_sale'].update({row.customer_file_name:True})
            else:
                self.env.context['remember_reorder_sale'].update({row.customer_file_name:False})
            q_row = quo_line_pool.browse(quo_l_rows[0])
            #context['cam_id'] = q_row.cam_check.id
            self.env.context['new_partner'] = rows.new_partner
            self.env.context['pcb_partner_delivery_time'] = rows.pcb_partner_delivery_time
            if row.product_no != '/':
                self.pool.get('cam.engineering.check').write(q_row.cam_check.id, {'product_no':row.product_no})
        return quo_pool.action_done([quo_id])
    
class confirm_product_no_line(osv.osv_memory):
    _name='confirm.product.no.line'
    _description="Confirm Product No Line"

    confirm_id = fields.Many2one('confirm.product.no', 'Confirm Reference', required=True, ondelete='cascade', index=True)
    product_no = fields.Char('Product No', size=100, required=False)
    customer_file_name = fields.Char('Customer File Name', size=100, required=True)