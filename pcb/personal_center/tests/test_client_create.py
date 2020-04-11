# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestClient(TransactionCase):

    def setUp(self):
        super(TestClient, self).setUp()
        a = 1

    def test_create(self):
        Todo = self.env['personal.center']
        task = Todo.create({'name': 'Test Task'})
        self.assertEqual(task.is_done, False)
