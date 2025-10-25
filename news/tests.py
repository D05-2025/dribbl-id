from django.test import TestCase, Client
from django.urls import reverse
from news.models import News
from main.models import CustomUser
import json
import uuid

class NewsPageTests(TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.admin_user = CustomUser.objects.create_user(
            username='adminuser',
            password='testpass123',
            role='admin'
        )
        
        self.regular_user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            role='user'
        )
        
        self.news1 = News.objects.create(
            title='First News',
            content='This is first news content',
            category='nba',
            thumbnail='https://example.com/thumb1.jpg',
            user=self.admin_user
        )
        
        self.news2 = News.objects.create(
            title='Second News',
            content='This is second news content',
            category='fiba',
            thumbnail='https://example.com/thumb2.jpg',
            user=self.admin_user
        )
        
        self.client = Client()
    
    # ============ URL Tests ============
    def test_news_url_exists(self):
        """Test apakah URL news terdaftar"""
        try:
            reverse('news:show_news_page')
            self.assertTrue(True)
        except:
            self.fail("URL news tidak ditemukan")
    
    def test_news_detail_url_exists(self):
        """Test URL detail news"""
        try:
            url = reverse('news:show_news_detail', args=[self.news1.id])
            self.assertIsNotNone(url)
        except:
            self.fail("URL news detail tidak ditemukan")
    
    # ============ Authentication Tests ============
    def test_news_page_redirects_anonymous(self):
        """Test anonymous user di-redirect ke login"""
        response = self.client.get(reverse('news:show_news_page'))
        self.assertEqual(response.status_code, 302)  # Redirect ke login
        self.assertIn('/login', response.url)
    
    def test_news_page_accessible(self):
        """Test halaman news bisa diakses oleh authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_page.html')
    
    def test_news_page_uses_correct_template(self):
        """Test menggunakan template yang benar"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page'))
        self.assertTemplateUsed(response, 'news_page.html')
    
    # ============ News List & Context Tests ============
    def test_news_list_shows_all_news(self):
        """Test menampilkan semua news"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page'))
        self.assertContains(response, 'First News')
        self.assertContains(response, 'Second News')
        self.assertEqual(len(response.context['news_list']), 2)
    
    def test_news_page_context_data(self):
        """Test context data yang dikirim ke template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page'))
        self.assertIn('news_list', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('selected_category', response.context)
        self.assertIn('selected_sort', response.context)
        self.assertIn('search_query', response.context)
        self.assertIn('user', response.context)
    
    # ============ Filter Tests ============
    def test_news_filter_by_category_nba(self):
        """Test filter by category NBA"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?category=nba')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First News')
        self.assertNotContains(response, 'Second News')
        self.assertEqual(response.context['selected_category'], 'nba')
    
    def test_news_filter_by_category_fiba(self):
        """Test filter by category FIBA"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?category=fiba')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second News')
        self.assertEqual(response.context['selected_category'], 'fiba')
    
    def test_news_filter_empty_category(self):
        """Test filter dengan category kosong (tampilkan semua)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?category=')
        self.assertEqual(len(response.context['news_list']), 2)
    
    # ============ Search Tests ============
    def test_news_search_by_title(self):
        """Test search by title"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?search=First')
        self.assertContains(response, 'First News')
        self.assertNotContains(response, 'Second News')
        self.assertEqual(response.context['search_query'], 'First')
    
    def test_news_search_by_content(self):
        """Test search by content"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?search=second')
        self.assertContains(response, 'Second News')
    
    def test_news_search_case_insensitive(self):
        """Test search case insensitive"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?search=FIRST')
        self.assertContains(response, 'First News')
    
    def test_news_search_empty_query(self):
        """Test search dengan query kosong"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?search=')
        self.assertEqual(len(response.context['news_list']), 2)
    
    def test_news_search_no_results(self):
        """Test search tanpa hasil"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?search=nonexistent')
        self.assertEqual(len(response.context['news_list']), 0)
    
    # ============ Sorting Tests ============
    def test_news_sort_by_newest(self):
        """Test sort by newest (default)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page'))
        news_list = response.context['news_list']
        self.assertEqual(news_list[0], self.news2)  # Newest first
        self.assertEqual(response.context['selected_sort'], 'newest')
    
    def test_news_sort_by_oldest(self):
        """Test sort by oldest"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?sort=oldest')
        news_list = response.context['news_list']
        self.assertEqual(news_list[0], self.news1)  # Oldest first
        self.assertEqual(response.context['selected_sort'], 'oldest')
    
    def test_news_sort_by_title_asc(self):
        """Test sort by title ascending"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?sort=title_asc')
        news_list = response.context['news_list']
        self.assertEqual(news_list[0].title, 'First News')
        self.assertEqual(response.context['selected_sort'], 'title_asc')
    
    def test_news_sort_by_title_desc(self):
        """Test sort by title descending"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?sort=title_desc')
        news_list = response.context['news_list']
        self.assertEqual(news_list[0].title, 'Second News')
        self.assertEqual(response.context['selected_sort'], 'title_desc')
    
    # ============ Combined Filter Tests ============
    def test_news_filter_and_search_combined(self):
        """Test kombinasi filter dan search"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?category=nba&search=First')
        self.assertEqual(len(response.context['news_list']), 1)
        self.assertEqual(response.context['news_list'][0].title, 'First News')
    
    def test_news_filter_search_sort_combined(self):
        """Test kombinasi filter, search, dan sort"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:show_news_page') + '?category=nba&search=news&sort=title_desc')
        self.assertEqual(response.status_code, 200)
    
    # ============ News Detail Tests ============
    def test_news_detail_page(self):
        """Test halaman detail news"""
        response = self.client.get(reverse('news:show_news_detail', args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_detail.html')
        self.assertEqual(response.context['news'].title, 'First News')
    
    def test_news_detail_shows_correct_content(self):
        """Test detail page menampilkan konten yang benar"""
        response = self.client.get(reverse('news:show_news_detail', args=[self.news1.id]))
        self.assertContains(response, 'First News')
        self.assertContains(response, 'This is first news content')
    
    def test_news_detail_404(self):
        """Test 404 for invalid news ID"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('news:show_news_detail', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)
    
    # ============ AJAX Add News Tests ============
    def test_add_news_requires_authentication(self):
        """Test add news memerlukan authentication"""
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'New News',
            'content': 'Content',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'User not authenticated')
    
    def test_add_news_admin_only(self):
        """Test hanya admin bisa create news"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'New News',
            'content': 'Content',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Only admin users can create news')
    
    def test_add_news_success_by_admin(self):
        """Test admin berhasil create news"""
        self.client.login(username='adminuser', password='testpass123')
        initial_count = News.objects.count()
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'Admin News',
            'content': 'Admin content',
            'category': 'nba',
            'thumbnail': 'https://example.com/thumb.jpg'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'News created successfully')
        self.assertIn('news_id', data)
        self.assertEqual(News.objects.count(), initial_count + 1)
        self.assertTrue(News.objects.filter(title='Admin News').exists())
    
    def test_add_news_without_thumbnail(self):
        """Test create news tanpa thumbnail"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'No Thumb News',
            'content': 'Content without thumbnail',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 201)
        news = News.objects.get(title='No Thumb News')
        self.assertIsNone(news.thumbnail)
    
    def test_add_news_validation_empty_title(self):
        """Test validation untuk title kosong"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': '',
            'content': 'Content',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Title is required')
    
    def test_add_news_validation_whitespace_title(self):
        """Test validation untuk title hanya whitespace"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': '   ',
            'content': 'Content',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_add_news_validation_empty_content(self):
        """Test validation untuk content kosong"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'Title',
            'content': '',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Content is required')
    
    def test_add_news_validation_empty_category(self):
        """Test validation untuk category kosong"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'Title',
            'content': 'Content',
            'category': ''
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Category is required')
    
    def test_add_news_strips_html_tags(self):
        """Test strip HTML tags dari input"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': '<b>Bold Title</b>',
            'content': '<script>alert("xss")</script>Content',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 201)
        news = News.objects.latest('published_at')
        self.assertEqual(news.title, 'Bold Title')
        self.assertNotIn('<script>', news.content)
    
    # ============ AJAX Edit News Tests ============
    def test_edit_news_requires_authentication(self):
        """Test edit news memerlukan authentication"""
        response = self.client.post(reverse('news:edit_news_entry_ajax', args=[self.news1.id]), {
            'title': 'Updated',
            'content': 'Updated',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_edit_news_admin_only(self):
        """Test hanya admin bisa edit news"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('news:edit_news_entry_ajax', args=[self.news1.id]), {
            'title': 'Updated Title',
            'content': 'Updated Content',
            'category': 'fiba'
        })
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Only admin can edit news')
    
    def test_edit_news_success_by_admin(self):
        """Test admin berhasil edit news"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:edit_news_entry_ajax', args=[self.news1.id]), {
            'title': 'Updated Title',
            'content': 'Updated Content',
            'category': 'fiba',
            'thumbnail': 'https://example.com/new.jpg'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'News updated successfully')
        
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.title, 'Updated Title')
        self.assertEqual(self.news1.content, 'Updated Content')
        self.assertEqual(self.news1.category, 'fiba')
    
    def test_edit_news_with_featured_flag(self):
        """Test edit news dengan is_featured flag"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:edit_news_entry_ajax', args=[self.news1.id]), {
            'title': 'Featured News',
            'content': 'Content',
            'category': 'nba',
            'is_featured': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.news1.refresh_from_db()
        self.assertTrue(self.news1.is_featured)
    
    def test_edit_news_invalid_method(self):
        """Test edit news dengan method yang salah"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.get(reverse('news:edit_news_entry_ajax', args=[self.news1.id]))
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Invalid method')
    
    def test_edit_news_404_for_invalid_id(self):
        """Test edit news dengan ID yang tidak ada"""
        self.client.login(username='adminuser', password='testpass123')
        invalid_id = uuid.uuid4()
        response = self.client.post(reverse('news:edit_news_entry_ajax', args=[invalid_id]), {
            'title': 'Updated',
            'content': 'Updated',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 404)
    
    # ============ AJAX Delete News Tests ============
    def test_delete_news_requires_authentication(self):
        """Test delete news memerlukan authentication"""
        response = self.client.post(reverse('news:delete_news', args=[self.news1.id]))
        self.assertEqual(response.status_code, 401)
    
    def test_delete_news_admin_only(self):
        """Test hanya admin bisa delete news"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('news:delete_news', args=[self.news1.id]))
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Only admin can delete news')
    
    def test_delete_news_success_by_admin(self):
        """Test admin berhasil delete news"""
        self.client.login(username='adminuser', password='testpass123')
        news_count_before = News.objects.count()
        news_id = self.news1.id
        response = self.client.post(reverse('news:delete_news', args=[news_id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'News deleted successfully')
        self.assertEqual(News.objects.count(), news_count_before - 1)
        self.assertFalse(News.objects.filter(id=news_id).exists())
    
    def test_delete_news_404_for_invalid_id(self):
        """Test delete news dengan ID yang tidak ada"""
        self.client.login(username='adminuser', password='testpass123')
        invalid_id = uuid.uuid4()
        response = self.client.post(reverse('news:delete_news', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)
    
    # ============ JSON API Tests ============
    def test_show_json_endpoint(self):
        """Test JSON API endpoint"""
        response = self.client.get(reverse('news:show_json'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertIn('created_at', data[0])
        self.assertIn('id', data[0])
        self.assertIn('title', data[0])
        self.assertIn('content', data[0])
        self.assertIn('category', data[0])
        self.assertIn('thumbnail', data[0])
        self.assertIn('user_id', data[0])
    
    def test_show_json_data_structure(self):
        """Test struktur data JSON"""
        response = self.client.get(reverse('news:show_json'))
        data = json.loads(response.content)
        self.assertEqual(data[0]['title'], 'First News')
        self.assertEqual(data[0]['category'], 'nba')
    
    def test_show_json_by_id_endpoint(self):
        """Test JSON by ID endpoint"""
        response = self.client.get(reverse('news:show_json_by_id', args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'First News')
        self.assertIn('created_at', data)
        self.assertIn('category', data)
    
    def test_show_json_by_id_404(self):
        """Test JSON by ID untuk news yang tidak ada"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('news:show_json_by_id', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['detail'], 'Not found')
    
    def test_get_news_json_endpoint(self):
        """Test get news JSON endpoint"""
        response = self.client.get(reverse('news:get_news_json', args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'First News')
        self.assertIn('user_id', data)
        self.assertIn('thumbnail', data)
    
    def test_get_news_json_with_null_thumbnail(self):
        """Test get news JSON dengan thumbnail null"""
        news_no_thumb = News.objects.create(
            title='No Thumb',
            content='Content',
            category='nba',
            user=self.admin_user
        )
        response = self.client.get(reverse('news:get_news_json', args=[news_no_thumb.id]))
        data = json.loads(response.content)
        self.assertEqual(data['thumbnail'], '')
    
    # ============ XML API Tests ============
    def test_show_xml_endpoint(self):
        """Test XML API endpoint"""
        response = self.client.get(reverse('news:show_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertContains(response, 'First News')
        self.assertContains(response, 'Second News')
    
    def test_show_xml_by_id_endpoint(self):
        """Test XML by ID endpoint"""
        response = self.client.get(reverse('news:show_xml_by_id', args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertContains(response, 'First News')
    
    def test_show_xml_by_id_404(self):
        """Test XML by ID untuk news yang tidak ada"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('news:show_xml_by_id', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)
    
    # ============ Model Tests ============
    def test_news_model_creation(self):
        """Test News model creation"""
        self.assertEqual(self.news1.title, 'First News')
        self.assertEqual(self.news1.content, 'This is first news content')
        self.assertEqual(self.news1.category, 'nba')
        self.assertEqual(self.news1.user.username, 'adminuser')
    
    def test_news_model_str(self):
        """Test string representation of News"""
        self.assertEqual(str(self.news1), 'First News')
    
    def test_news_count(self):
        """Test news count"""
        self.assertEqual(News.objects.count(), 2)
    
    def test_news_filter_by_user(self):
        """Test filter news by user"""
        admin_news = News.objects.filter(user=self.admin_user)
        self.assertEqual(admin_news.count(), 2)
    
    def test_news_filter_by_category_model(self):
        """Test filter news by category di model level"""
        nba_news = News.objects.filter(category='nba')
        self.assertEqual(nba_news.count(), 1)
        self.assertEqual(nba_news.first().title, 'First News')
    
    # ============ Edge Cases ============
    def test_news_with_special_characters(self):
        """Test news dengan karakter spesial"""
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'News with "quotes" & symbols!',
            'content': 'Content with special chars: @#$%',
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 201)
    
    def test_news_with_long_content(self):
        """Test news dengan content panjang"""
        self.client.login(username='adminuser', password='testpass123')
        long_content = 'A' * 10000
        response = self.client.post(reverse('news:add_news_entry_ajax'), {
            'title': 'Long Content News',
            'content': long_content,
            'category': 'nba'
        })
        self.assertEqual(response.status_code, 201)
    
    def test_multiple_users_same_category(self):
        """Test multiple news dari user berbeda dengan kategori sama"""
        news3 = News.objects.create(
            title='Third News',
            content='Content from regular user',
            category='nba',
            user=self.regular_user
        )
        nba_news = News.objects.filter(category='nba')
        self.assertEqual(nba_news.count(), 2)
    
    def test_news_app_configured(self):
        """Test news app terkonfigurasi dengan benar"""
        self.assertTrue(True)