from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Player

User = get_user_model()

class PlayerTests(TestCase):
    def setUp(self):
        # Buat user admin dan login
        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin123",
            role="admin"
        )
        self.client = Client()
        self.client.login(username="admin", password="admin123")

        # Buat contoh player
        self.player = Player.objects.create(
            name="LeBron James",
            team="Lakers",
            position="SF",
            points_per_game=27.0,
            assists_per_game=7.0,
            rebounds_per_game=8.0,
        )

    def test_player_list_view(self):
        """Halaman list pemain bisa diakses"""
        response = self.client.get(reverse('players:player_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LeBron James")

    def test_add_player_view(self):
        """Admin bisa menambah player baru"""
        response = self.client.post(reverse('players:add_player'), {
            'name': 'Stephen Curry',
            'team': 'Warriors',
            'position': 'PG',
            'points_per_game': 30,
            'assists_per_game': 6,
            'rebounds_per_game': 5,
        })
        self.assertEqual(response.status_code, 302)  # redirect sukses
        self.assertTrue(Player.objects.filter(name="Stephen Curry").exists())

    def test_edit_player_view(self):
        """Admin bisa mengedit player"""
        response = self.client.post(
            reverse('players:edit_player', args=[self.player.id]),
            {
                'name': 'LeBron James',
                'team': 'Lakers',
                'position': 'PF',  # ubah posisi
                'points_per_game': 28,
                'assists_per_game': 8,
                'rebounds_per_game': 9,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.player.refresh_from_db()
        self.assertEqual(self.player.position, "PF")

    def test_delete_player_view(self):
        """Admin bisa menghapus player"""
        response = self.client.post(reverse('players:delete_player', args=[self.player.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Player.objects.filter(id=self.player.id).exists())

    def test_str_method(self):
        """Cek __str__ di model"""
        self.assertEqual(str(self.player), "LeBron James")
