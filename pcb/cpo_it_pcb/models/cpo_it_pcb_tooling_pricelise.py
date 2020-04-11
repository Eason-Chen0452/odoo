# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import odoo.addons.decimal_precision as dp

AVAILABLE_PRICE_TYPE = [
    ('item', 'Item'),
    ('csize', 'Size(cm²)'),
    ('msize', 'Size(㎡)'),
    ('pcs', 'PCS'),
    ('set', 'SET'),
]


class pcb_tooling_pricelist(models.Model):
    _name = "pcb.tooling.pricelist"
    _description = "Price List of Test Tooling"
    _order = "min_test_points"

    min_test_points = fields.Integer('Min Test Points')
    max_test_points = fields.Integer('Max Test Points')
    price_type = fields.Selection([('item', 'Item'),
                                   ('point', 'Point'), ], 'Price Type', required=True)
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'))
    company_id = fields.Many2one('res.company', 'Company')
    memo = fields.Text('Memo')
    active = fields.Boolean('Active',
                             help="If unchecked, it will allow you to hide the pricelist without removing it.")

    _defaults = {
        'min_test_points': 0.0,
        'max_test_points': 0.0,
        'price_type': 'point',
        'price': 0.0,
        'active': lambda *a: 1,
    }

    def _check_test_points(self, cr, uid, ids, context=None):
        context = context or {}

        obj_etest = self.browse(cr, uid, ids[0], context=context)
        if obj_etest.min_test_points > obj_etest.max_test_points:
            return False
        min_point = obj_etest.min_test_points
        max_point = obj_etest.max_test_points
        cr.execute(
            'SELECT count(id) FROM pcb_tooling_pricelist WHERE max_test_points>%f AND min_test_points<%f AND id != %s' % (
            min_point, max_point, ids[0]))

        etest_rows = cr.fetchone()[0] or 0.0

        if etest_rows:
            return False
        return True

    _constraints = [
        (_check_test_points, 'Error!\nThe row test points overlap other rows.', ['min_test_points', 'max_test_points'])
    ]

    _sql_constraints = [
        ('tooling_min_max_points_uniq', 'unique(min_test_points, max_test_points)',
         'Min Test Points and Max Test Points must be unique in pcb tooling price list!'),
    ]


class pcb_etest_pricelist(models.Model):
    _name = "pcb.etest.pricelist"
    _description = "Price List of ETest"
    _order = "min_test_points"

    min_test_points = fields.Integer('Min Test Points')
    max_test_points = fields.Integer('Max Test Points')
    price_type = fields.Selection([('item', 'Item'),
                                    ('point', 'Point'), ], 'Price Type', required=True)
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'))
    company_id = fields.Many2one('res.company', 'Company')
    memo = fields.Text('Memo')
    active = fields.Boolean('Active',
                             help="If unchecked, it will allow you to hide the pricelist without removing it.")

    _defaults = {
        'min_test_points': 0.0,
        'max_test_points': 0.0,
        'price_type': 'point',
        'price': 0.0,
        'active': lambda *a: 1,
    }

    def _check_test_points(self, cr, uid, ids, context=None):
        context = context or {}

        obj_etest = self.browse(cr, uid, ids[0], context=context)
        if obj_etest.min_test_points > obj_etest.max_test_points:
            return False
        min_point = obj_etest.min_test_points
        max_point = obj_etest.max_test_points
        cr.execute(
            'SELECT count(id) FROM pcb_etest_pricelist WHERE max_test_points>%f AND min_test_points<%f AND id != %s' % (
            min_point, max_point, ids[0]))

        etest_rows = cr.fetchone()[0] or 0.0

        if etest_rows:
            return False
        return True

    _constraints = [
        (_check_test_points, 'Error!\nThe row test points overlap other rows.', ['min_test_points', 'max_test_points'])
    ]

    _sql_constraints = [
        ('etest_min_max_points_uniq', 'unique(min_test_points, max_test_points)',
         'Min Test Points and Max Test Points must be unique in etest price list!'),
    ]


class pcb_film_pricelist(models.Model):
    _name = "pcb.film.pricelist"
    _description = "Price List of Film"
    _order = "min_size, max_size"

    min_size = fields.Float('Min Size', required=True, digits=dp.get_precision('size'))
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'))
    film_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Film Fee Type', required=True)
    film_fee = fields.Float('Film Fee', required=True, digits=dp.get_precision('Product Price'))
    company_id = fields.Many2one('res.company', 'Company')
    memo = fields.Text('Memo')
    active = fields.Boolean('Active',
                             help="If unchecked, it will allow you to hide the pricelist without removing it.")

    _defaults = {
        'min_size': 0.0,
        'max_size': 0.0,
        'film_fee_type': 'item',
        'film_fee': 0.0,
        'active': lambda *a: 1,
    }

    def _check_film_size(self, cr, uid, ids, context=None):
        context = context or {}

        obj_film = self.browse(cr, uid, ids[0], context=context)
        if obj_film.min_size > obj_film.max_size:
            return False
        min_size = obj_film.min_size
        max_size = obj_film.max_size
        cr.execute('SELECT count(id) FROM pcb_film_pricelist WHERE max_size>%f AND min_size<%f AND id != %s' % (
        min_size, max_size, ids[0]))

        eline_rows = cr.fetchone()[0] or 0.0

        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_film_size, 'Error!\nThe row film min size and max size overlap other rows.', ['min_size', 'max_size'])
    ]

    _sql_constraints = [
        ('film_min_max_size_uniq', 'unique(min_size, max_size)',
         'Film min size and max size must be unique in pcb film price list!'),
    ]



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: