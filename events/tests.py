from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time, datetime
from main.models import CustomUser
from events.models import Event

class EventViewsTestCase(TestCase):
    def setUp(self):
        # Buat client dan admin user
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

        # Buat contoh event
        self.event = Event.objects.create(
            title="Test Event",
            description="Deskripsi event",
            date=datetime(2025, 10, 10, 15, 0),
            is_public=True,
            image_url="https://example.com/image.jpg",
            location="Jakarta",
            time="15:00",
            created_by=self.admin_user  # ✅ foreign key yang valid
        )

        # Simulasikan sesi login sebagai admin
        session = self.client.session
        session['user_id'] = str(self.admin_user.id)
        session['role'] = 'admin'
        session.save()

    def test_event_list_admin_view(self):
        """Admin bisa melihat semua event"""
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

    def test_create_event_view(self):
        """Admin bisa membuat event baru"""
        response = self.client.post(reverse('events:create_event'), {
            'title': 'Event Baru',
            'description': 'Deskripsi baru',
            'date': '2025-10-15',
            'is_public': 'on',
            'image_url': 'https://example.com/new.jpg',
            'location': 'Bandung',
            'time': '14:00'
        })
        self.assertEqual(response.status_code, 302)  # redirect sukses
        self.assertTrue(Event.objects.filter(title='Event Baru').exists())

    def test_edit_event_view(self):
        """Admin bisa edit event"""
        response = self.client.post(reverse('events:edit_event', args=[self.event.id]), {
            'title': 'Event Diedit',
            'description': 'Deskripsi update',
            'date': '2025-10-20',
            'is_public': 'on',
            'image_url': 'https://example.com/edited.jpg',
            'location': 'Bali',
            'time': '10:00'
        })
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Event Diedit')

    def test_delete_event_view(self):
        """Admin bisa menghapus event"""
        response = self.client.get(reverse('events:delete_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_unauthorized_create_event(self):
        """User non-admin tidak boleh membuat event"""
        session = self.client.session
        session['user_id'] = str(self.normal_user.id)
        session['role'] = 'user'
        session.save()

        response = self.client.post(reverse('events:create_event'), {
            'title': 'Event Curang',
            'description': 'Harusnya gagal',
            'date': '2025-10-25',
        })
        self.assertEqual(response.status_code, 403)
