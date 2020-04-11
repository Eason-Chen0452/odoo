##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
{
    "name" : "Sale Quotation For PCB",
    "version" : "1.0",
    'sequence': 14,
    "category" : "Sales Management",
    'summary': 'Quotations For PCB',
    "description": """
Manage sales quotations and orders
==================================

This application allows you to manage your sales goals in an effective and efficient manner by keeping track of all sales orders and history.

It handles the full sales workflow:

* **Quotation** -> **Sales order** -> **Invoice**

Preferences (only with Warehouse Management installed)
------------------------------------------------------

If you also installed the Warehouse Management, you can deal with the following preferences:

* Shipping: Choice of delivery at once or partial delivery
* Invoicing: choose how invoices will be paid
* Incoterms: International Commercial terms

You can choose flexible invoicing methods:

* *On Demand*: Invoices are created manually from Sales Orders when needed
* *On Delivery Order*: Invoices are generated from picking (delivery)
* *Before Delivery*: A Draft invoice is created and must be paid before delivery


The Dashboard for the Sales Manager will include
------------------------------------------------
* My Quotations
* Monthly Turnover (Graph)
    """,
    "author": "Eason Chen",
    "website": "http://www.chinapcbone.cn",
    "depends": [
        'base',
        'cpo_it_pcb',
        'account',
        'sale',
        'cpo_offer_base'
        ],
    "data": [
        'security/sale_quotation_security.xml',
        'security/ir.model.access.csv',
        'views/sale_quotation.xml',
        'views/sale_quotation_line.xml',
        'views/sale_order.xml',
        'views/sale_quotation_freight.xml',
        'views/sale_quotation_sequence.xml',
        'views/sale_pcb_rfq_workflow.xml',
        'views/sale_pcb_rfq_data.xml',
        'views/order_notice_views.xml',
        'views/specific_product_offers.xml',
        'data/country_freight_data.xml',
        'data/country_freight_data2.xml',
        'data/order_notice_data.xml',
        'data/email_template.xml',
        ],
    "demo": [],
    "test": [],
    'installable': True,
    'auto_install': False,
}
##############################################################################

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
