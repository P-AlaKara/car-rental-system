#!/usr/bin/env python3
"""
Regression tests for car documents page to ensure URLs are built properly.

This covers the bug where a single string was iterated character-by-character
and rendered as multiple broken document cards. We assert exactly one card is
rendered and the URL appears intact for both string and dict document inputs.
"""

import os
import unittest

from app import create_app, db
from app.models import User, Role
from app.models.car import Car, CarCategory, CarStatus


class DocumentsViewTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()
        cls.ctx = cls.app.app_context()
        cls.ctx.push()
        db.create_all()

        # Create admin user
        admin = User(
            email='admin@test.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            role=Role.ADMIN,
            phone='+1000000000',
        )
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        cls.admin_id = admin.id

        # Login helper
        with cls.client as c:
            c.post('/auth/login', data={'email': 'admin@test.com', 'password': 'password'}, follow_redirects=True)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.ctx.pop()

    def _create_car(self, plate: str) -> Car:
        car = Car(
            make='Test',
            model='Car',
            year=2024,
            license_plate=plate,
            vin=f'VIN{plate}',
            category=CarCategory.COMPACT,
            seats=5,
            daily_rate=50.0,
            status=CarStatus.AVAILABLE,
        )
        db.session.add(car)
        db.session.commit()
        return car

    def test_single_string_document_renders_once_with_full_url(self):
        car = self._create_car('DOCS001')
        # Legacy single string value
        car.documents = '/uploads/car-documents/test_doc.pdf'
        db.session.commit()

        resp = self.client.get(f'/admin/fleet/{car.id}/documents')
        self.assertEqual(resp.status_code, 200)

        html = resp.data.decode('utf-8')
        # Exactly one card should render
        self.assertEqual(html.count('class="image-card"'), 1)
        # URL should appear intact (not split into characters)
        self.assertIn('/uploads/car-documents/test_doc.pdf', html)
        # May appear multiple times (img src, onclick, anchor). Ensure not exploded per character
        self.assertGreaterEqual(html.count('/uploads/car-documents/test_doc.pdf'), 1)

    def test_single_dict_document_renders_once_with_full_url(self):
        car = self._create_car('DOCS002')
        # Dict with metadata
        car.documents = {
            'url': '/uploads/car-documents/image1.png',
            'name': 'image1.png',
            'mime': 'image/png',
        }
        db.session.commit()

        resp = self.client.get(f'/admin/fleet/{car.id}/documents')
        self.assertEqual(resp.status_code, 200)

        html = resp.data.decode('utf-8')
        self.assertEqual(html.count('class="image-card"'), 1)
        self.assertIn('/uploads/car-documents/image1.png', html)
        self.assertGreaterEqual(html.count('/uploads/car-documents/image1.png'), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

