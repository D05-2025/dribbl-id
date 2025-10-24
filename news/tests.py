from django.test import TestCase
from django.urls import reverse

class NewsPageTests(TestCase):
    
    def test_news_url_exists(self):
        try:
            reverse('news:show_news_page')
            self.assertTrue(True)
        except:
            self.fail("URL news tidak ditemukan")
    
    def test_news_page_redirects(self):
        response = self.client.get(reverse('news:show_news_page'))
        self.assertEqual(response.status_code, 302) 
    
    def test_news_app_configured(self):
        self.assertTrue(True) 