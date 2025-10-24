from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime
from authentication.models import CustomUser
from events.models import Event


class EventViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(
            username='admin123',
            password='testpass',
            role='admin'
        )
        self.normal_user = CustomUser.objects.create_user(
            username='user123',
            password='testpass',
            role='user'
        )

        self.event = Event.objects.create(
            title="Test Event",
            description="Deskripsi event",
            date=datetime(2025, 10, 10, 15, 0),
            is_public=True,
            image_url="https://example.com/image.jpg",
            location="Jakarta",
            time="15:00",
            created_by=self.admin_user
        )

    # -------------------------------
    # EVENT LIST
    # -------------------------------
    def test_event_list_requires_login(self):
        """User tanpa login diarahkan ke login"""
        response = self.client.get(reverse('events:event_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_event_list_admin_view(self):
        """Admin bisa melihat semua event"""
        session = self.client.session
        session['user_id'] = str(self.admin_user.id)
        session['role'] = 'admin'
        session.save()
        response = self.client.get(reverse('events:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_event_list_user_view(self):
        """User biasa hanya melihat event publik"""
        session = self.client.session
        session['user_id'] = str(self.normal_user.id)
        session['role'] = 'user'
        session.save()
        response = self.client.get(reverse('events:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_event_list_ajax(self):
        """Admin dapat data JSON via AJAX"""
        session = self.client.session
        session['user_id'] = str(self.admin_user.id)
        session['role'] = 'admin'
        session.save()
        response = self.client.get(
            reverse('events:event_list'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('events', response.json())

    # -------------------------------
    # CREATE EVENT
    # -------------------------------
    def test_create_event_unauthenticated(self):
        """User belum login tidak bisa membuat event"""
        response = self.client.post(reverse('events:create_event'), {
            'title': 'Event Tak Login'
        })
        self.assertEqual(response.status_code, 302)

    def test_create_event_forbidden_for_user(self):
        """User biasa tidak boleh membuat event"""
        session = self.client.session
        session['user_id'] = str(self.normal_user.id)
        session['role'] = 'user'
        session.save()
        response = self.client.post(reverse('events:create_event'), {
            'title': 'Event User',
            'description': 'Harus gagal',
            'date': '2025-10-25',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_create_event_success_admin(self):
        """Admin bisa membuat event (via AJAX)"""
        session = self.client.session
        session['user_id'] = str(self.admin_user.id)
        session['role'] = 'admin'
        session.save()
        response = self.client.post(reverse('events:create_event'), {
            'title': 'Event Baru',
            'description': 'Deskripsi baru',
            'date': '2025-10-15',
            'is_public': 'on',
            'image_url': 'https://example.com/new.jpg',
            'location': 'Bandung',
            'time': '14:00'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Event.objects.filter(title='Event Baru').exists())

    # -------------------------------
    # EDIT EVENT
    # -------------------------------
    def test_edit_event_unauthorized(self):
        """User non-admin tidak bisa edit event"""
        session = self.client.session
        session['user_id'] = str(self.normal_user.id)
        session['role'] = 'user'
        session.save()
        response = self.client.post(reverse('events:edit_event', args=[self.event.id]), {
            'title': 'Coba Edit',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_edit_event_success_admin(self):
        """Admin bisa edit event"""
        session = self.client.session
        session['user_id'] = str(self.admin_user.id)
        session['role'] = 'admin'
        session.save()
        response = self.client.post(reverse('events:edit_event', args=[self.event.id]), {
            'title': 'Event Diedit',
            'description': 'Deskripsi update',
            'date': '2025-10-20',
            'is_public': 'on',
            'image_url': 'https://example.com/edited.jpg',
            'location': 'Bali',
            'time': '10:00'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Event Diedit')

    # -------------------------------
    # DELETE EVENT
    # -------------------------------
    def test_delete_event_unauthorized(self):
        """User biasa tidak bisa hapus event"""
        session = self.client.session
        session['user_id'] = str(self.normal_user.id)
        session['role'] = 'user'
        session.save()
        response = self.client.post(reverse('events:delete_event', args=[self.event.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_delete_event_success_admin(self):
        """Admin bisa hapus event"""
        session = self.client.session
        session['user_id'] = str(self.admin_user.id)
        session['role'] = 'admin'
        session.save()
        response = self.client.post(reverse('events:delete_event', args=[self.event.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
