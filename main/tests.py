from django.test import TestCase, Client
from django.urls import reverse
from main.models import CustomUser, CustomUserManager
from django.contrib.auth.hashers import make_password
import uuid

class CustomUserModelTests(TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()

    def test_create_user_success(self):
        """Test create user dengan manager"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_without_username(self):
        """Test create user tanpa username (harus error)"""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(username='', password='testpass123')
        self.assertEqual(str(context.exception), 'Username harus diisi')
    
    def test_create_user_with_extra_fields(self):
        """Test create user dengan extra fields"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            bio='Test bio',
            role='admin'
        )
        self.assertEqual(user.bio, 'Test bio')
        self.assertEqual(user.role, 'admin')
    
    def test_create_superuser(self):
        """Test create superuser"""
        superuser = CustomUser.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.role, 'admin')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
    
    # ============ CustomUser Model Tests ============
    def test_user_model_str(self):
        """Test string representation"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            role='user'
        )
        self.assertEqual(str(user), 'testuser (user)')
    
    def test_user_uuid_primary_key(self):
        """Test UUID sebagai primary key"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertIsInstance(user.id, uuid.UUID)
    
    def test_user_has_perm_admin(self):
        """Test has_perm untuk admin"""
        admin = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.assertTrue(admin.has_perm('any.permission'))
    
    def test_user_has_perm_regular_user(self):
        """Test has_perm untuk regular user"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            role='user'
        )
        self.assertFalse(user.has_perm('any.permission'))
    
    def test_user_has_perm_superuser(self):
        """Test has_perm untuk superuser"""
        superuser = CustomUser.objects.create_superuser(
            username='superuser',
            password='super123'
        )
        self.assertTrue(superuser.has_perm('any.permission'))
    
    def test_user_has_module_perms_admin(self):
        """Test has_module_perms untuk admin"""
        admin = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.assertTrue(admin.has_module_perms('any_app'))
    
    def test_user_has_module_perms_regular_user(self):
        """Test has_module_perms untuk regular user"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            role='user'
        )
        self.assertFalse(user.has_module_perms('any_app'))
    
    def test_user_role_choices(self):
        """Test role choices"""
        self.assertEqual(len(CustomUser.ROLE_CHOICES), 2)
        role_values = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        self.assertIn('admin', role_values)
        self.assertIn('user', role_values)
    
    def test_user_optional_fields(self):
        """Test optional fields (bio, profile_picture)"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            bio='Test bio',
            profile_picture='https://example.com/pic.jpg'
        )
        self.assertEqual(user.bio, 'Test bio')
        self.assertEqual(user.profile_picture, 'https://example.com/pic.jpg')
    
    def test_user_without_optional_fields(self):
        """Test user tanpa optional fields"""
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertIsNone(user.bio)
        self.assertIsNone(user.profile_picture)


class MainViewsTests(TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            role='user'
        )
        self.admin = CustomUser.objects.create_user(
            username='adminuser',
            password='admin123',
            role='admin'
        )
    
    # ============ Show Main Tests ============
    def test_show_main_page(self):
        """Test homepage bisa diakses"""
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')
    
    def test_show_main_context(self):
        """Test context data di homepage"""
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.context['title'], 'DRIBBL.ID')
        self.assertEqual(response.context['welcome_text'], 'Welcome to DRIBBL.ID')
        self.assertEqual(response.context['subtitle'], 'The biggest Indonesian basketball community')
    
    def test_show_main_contains_content(self):
        """Test homepage mengandung konten yang benar"""
        response = self.client.get(reverse('main:show_main'))
        self.assertContains(response, 'DRIBBL.ID')
        self.assertContains(response, 'Welcome to DRIBBL.ID')
    
    # ============ Register Tests ============
    def test_register_page_get(self):
        """Test halaman register bisa diakses"""
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_register_success(self):
        """Test register user baru berhasil"""
        response = self.client.post(reverse('main:register'), {
            'username': 'newuser',
            'password': 'newpass123',
            'role': 'user'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('main:login'))
        
        # Verify user created
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())
        new_user = CustomUser.objects.get(username='newuser')
        self.assertEqual(new_user.role, 'user')
        self.assertTrue(new_user.check_password('newpass123'))
    
    def test_register_default_role(self):
        """Test register tanpa role (default ke user)"""
        response = self.client.post(reverse('main:register'), {
            'username': 'defaultuser',
            'password': 'pass123'
        })
        user = CustomUser.objects.get(username='defaultuser')
        self.assertEqual(user.role, 'user')
    
    def test_register_as_admin(self):
        """Test register dengan role admin"""
        response = self.client.post(reverse('main:register'), {
            'username': 'newadmin',
            'password': 'admin123',
            'role': 'admin'
        })
        user = CustomUser.objects.get(username='newadmin')
        self.assertEqual(user.role, 'admin')
    
    def test_register_empty_username(self):
        """Test register dengan username kosong"""
        response = self.client.post(reverse('main:register'), {
            'username': '',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:register'))
        
        # Verify user not created
        self.assertFalse(CustomUser.objects.filter(username='').exists())
    
    def test_register_empty_password(self):
        """Test register dengan password kosong"""
        response = self.client.post(reverse('main:register'), {
            'username': 'testuser2',
            'password': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:register'))
        
        # Verify user not created
        self.assertFalse(CustomUser.objects.filter(username='testuser2').exists())
    
    def test_register_duplicate_username(self):
        """Test register dengan username yang sudah ada"""
        response = self.client.post(reverse('main:register'), {
            'username': 'testuser',  # Already exists in setUp
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:register'))
        
        # Verify only one user with this username
        self.assertEqual(CustomUser.objects.filter(username='testuser').count(), 1)
    
    # ============ Login Tests ============
    def test_login_page_get(self):
        """Test halaman login bisa diakses"""
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_login_success(self):
        """Test login berhasil"""
        response = self.client.post(reverse('main:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:show_main'))
        
        # Verify session created
        self.assertEqual(self.client.session['username'], 'testuser')
        self.assertEqual(self.client.session['role'], 'user')
        self.assertIn('user_id', self.client.session)
        
        # Verify cookie set
        self.assertIn('last_login', response.cookies)
    
    def test_login_admin(self):
        """Test login sebagai admin"""
        response = self.client.post(reverse('main:login'), {
            'username': 'adminuser',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['role'], 'admin')
    
    def test_login_wrong_password(self):
        """Test login dengan password salah"""
        response = self.client.post(reverse('main:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertTemplateUsed(response, 'login.html')
        
        # Verify session not created
        self.assertNotIn('username', self.client.session)
    
    def test_login_nonexistent_user(self):
        """Test login dengan user yang tidak ada"""
        response = self.client.post(reverse('main:login'), {
            'username': 'nonexistent',
            'password': 'anypassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        
        # Verify session not created
        self.assertNotIn('username', self.client.session)
    
    def test_login_empty_username(self):
        """Test login dengan username kosong"""
        response = self.client.post(reverse('main:login'), {
            'username': '',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', self.client.session)
    
    def test_login_empty_password(self):
        """Test login dengan password kosong"""
        response = self.client.post(reverse('main:login'), {
            'username': 'testuser',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', self.client.session)
    
    def test_login_empty_credentials(self):
        """Test login tanpa credentials"""
        response = self.client.post(reverse('main:login'), {})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', self.client.session)
    
    # ============ Logout Tests ============
    def test_logout_user(self):
        """Test logout user"""
        # Login first
        self.client.post(reverse('main:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verify logged in
        self.assertIn('username', self.client.session)
        
        # Logout
        response = self.client.get(reverse('main:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:show_main'))
        
        # Verify session cleared
        self.assertNotIn('username', self.client.session)
        
        # Verify cookie deleted
        self.assertEqual(response.cookies['last_login'].value, '')
    
    def test_logout_without_login(self):
        """Test logout tanpa login terlebih dahulu"""
        response = self.client.get(reverse('main:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:show_main'))
    
    # ============ URL Tests ============
    def test_main_url_exists(self):
        """Test URL main terdaftar"""
        try:
            reverse('main:show_main')
            self.assertTrue(True)
        except:
            self.fail("URL main tidak ditemukan")
    
    def test_register_url_exists(self):
        """Test URL register terdaftar"""
        try:
            reverse('main:register')
            self.assertTrue(True)
        except:
            self.fail("URL register tidak ditemukan")
    
    def test_login_url_exists(self):
        """Test URL login terdaftar"""
        try:
            reverse('main:login')
            self.assertTrue(True)
        except:
            self.fail("URL login tidak ditemukan")
    
    def test_logout_url_exists(self):
        """Test URL logout terdaftar"""
        try:
            reverse('main:logout')
            self.assertTrue(True)
        except:
            self.fail("URL logout tidak ditemukan")
    
    # ============ Integration Tests ============
    def test_register_then_login(self):
        """Test flow: register -> login"""
        # Register
        self.client.post(reverse('main:register'), {
            'username': 'flowuser',
            'password': 'flow123'
        })
        
        # Login
        response = self.client.post(reverse('main:login'), {
            'username': 'flowuser',
            'password': 'flow123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['username'], 'flowuser')
    
    def test_login_logout_flow(self):
        """Test flow: login -> logout"""
        # Login
        self.client.post(reverse('main:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertIn('username', self.client.session)
        
        # Logout
        self.client.get(reverse('main:logout'))
        self.assertNotIn('username', self.client.session)
    
    def test_session_persistence(self):
        """Test session tetap ada setelah login"""
        self.client.post(reverse('main:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Access main page
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.status_code, 200)
        
        # Session should still exist
        self.assertIn('username', self.client.session)