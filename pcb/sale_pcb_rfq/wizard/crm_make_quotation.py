# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.osv import osv


class crm_make_quotation(osv.osv_memory):
    """ Make sale  quotation for crm """

    _name = "crm.make.quotation"
    _description = "Make Quotation"

    def _selectLead(self, context=None):
        """
        This function gets default value for partner_id field.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary for contextual values
        @return: default value of partner_id field.
        """
        if context is None:
            context = {}

        #lead_obj = self.pool.get('crm.lead')
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            return False

        #lead = lead_obj.read(cr, uid, active_id, ['partner_id'])
        return active_id

    def view_init(self, fields_list):
        return super(crm_make_quotation, self).view_init(fields_list)

    def _get_currency(self):
        comp = self.pool.get('res.users').browse(self).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search([])[0]
            comp = self.pool.get('res.company').browse(comp_id)
        return comp.currency_id.id

    def makeOrder(self):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        self.env.context.pop('default_state', False)
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.quotation')
        partner_obj = self.pool.get('res.partner')
        data = self.env.context and self.env.context.get('active_ids', []) or []

        for make in self.browse(self.ids):
            #partner = make.partner_id
            partner = make.lead_id.partner_id
            lead = make.lead_id
            partner_addr = partner and partner_obj.address_get([partner.id],
                    ['default', 'invoice', 'delivery', 'contact']) or {}
            #pricelist = partner.property_product_pricelist.id
            
            #pricelist = partner.property_sale_pcb_pricelist and partner.property_sale_pcb_pricelist.id or False            
            pricelist = False
            
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(data):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get([partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    #'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'shop_id': make.shop_id.id,
                    #'partner_id': partner.id,
                    'lead_id': lead.id,
                    'pricelist_id': pricelist,
                    #'partner_invoice_id': partner_addr['invoice'],
                    #'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.Date.context_today(self),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                    "currency_id": self._get_currency(),
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id
                new_id = sale_obj.create(vals)
                sale_order = sale_obj.browse(new_id)
                case_obj.write([case.id], {'ref': 'sale.quotation,%s' % new_id})
                new_ids.append(new_id)
                if case.type == 'lead':
                    message = _("Leads has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                    sale_obj.write(new_id, {'origin': 'Leads:%s' % str(case.id)})
                elif case.type == 'opportunity':
                    message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                    sale_obj.write(new_id, {'origin': 'Opportunity:%s' % str(case.id)})
                case.message_post(body=message)
            if make.close:
                case_obj.case_close(data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            model_data = self.pool.get('ir.model.data')
            form_view = model_data.get_object_reference('sale_pcb_rfq', 'view_sale_quotation_form')[1]
            context = ({'partner':True,'lead':False})
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.quotation',
                    #'view_id': False,
                    'view_id':form_view,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0],
                    'context':context,
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.quotation',
                    #'view_id': False,
                    'view_id':form_view,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids,
                    'context':context,
                }
            return value

    def _get_shop_id(self):
        cmpny_id = self.pool.get('res.users')._get_company()
        shop = self.pool.get('sale.shop').search([('company_id', '=', cmpny_id)])
        return shop and shop[0] or False

    shop_id = fields.Many2one('sale.shop', 'Shop', required=True)
    #'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain=[('customer','=',True)]),
    lead_id = fields.Many2one('crm.lead', 'Lead', required=True)
    close = fields.Boolean('Mark Won', help='Check this to close the opportunity after having created the sales order.')

    _defaults = {
        'shop_id': _get_shop_id,
        'close': False,
        'lead_id': _selectLead,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
