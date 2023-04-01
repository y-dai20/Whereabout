from django.test import TestCase
from django.urls import reverse_lazy


from base.models.account_models import User
from base.models.post_models import Post

class LoggedInTestCase(TestCase):

    def setUp(self):
        # テスト用アカウントの作成
        self.password = 'password123'
        self.test_user = User.objects.create_user(
            username='test_user01',
            email='test_user01@email.com',
            password=self.password
        )
        # テスト用アカウントのログイン
        self.client.login(username=self.test_user.username, email=self.test_user.email, password=self.password)

class TestPostCreate(LoggedInTestCase):
    
    def test_create_post_success(self):
        # Postデータを作成
        params = {
            'title':'test title',
            'text':'test text',
            'room_id':'',
            'source':'',
            'tags':'',
            'imgs':'',
            'videos':'',
        }
        response = self.client.post(reverse_lazy('post'), params)
        print(response)
        # データベースへ登録されたことの確認
        self.assertEqual(Post.objects.active(title=params['title']).count(), 1)
