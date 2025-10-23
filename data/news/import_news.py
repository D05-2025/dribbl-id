# import_news.py
import csv
import os
import django
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dribbl_id.settings')
django.setup()

# ⚠️ IMPORT CUSTOM USER MODEL, BUKAN User bawaan ⚠️
from django.contrib.auth import get_user_model
from news.models import News
from django.utils import timezone

# Dapatkan Custom User model
CustomUser = get_user_model()

def import_news():
    csv_path = 'news_data.csv'
    
    print(f"📁 Membaca file: {csv_path}")
    
    try:
        # Cari user admin di Custom User model
        admin_users = CustomUser.objects.filter(role='admin')  # Sesuaikan field role-nya
        if admin_users.exists():
            user = admin_users.first()
            print(f"👤 Pakai admin user: {user.username} (ID: {user.id})")
        else:
            # Fallback ke user pertama
            user = CustomUser.objects.first()
            if user:
                print(f"👤 Pakai user: {user.username} (ID: {user.id})")
            else:
                print("❌ Tidak ada user di database!")
                return
                
    except Exception as e:
        print(f"❌ Error mendapatkan user: {str(e)}")
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                print(f"📰 Memproses: {row['title'][:50]}...")
                
                news = News(
                    title=row['title'],
                    category=row['category'],
                    content=row['content'],
                    thumbnail=row['thumbnail'],
                    user=user,  # ← Pakai Custom User
                    published_at=timezone.now()
                )
                news.save()
                count += 1
            
            print(f"🎉 SUKSES! {count} berita berhasil diimport!")
            
    except FileNotFoundError:
        print(f"❌ File {csv_path} tidak ditemukan")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    import_news()