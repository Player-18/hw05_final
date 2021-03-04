from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class UrlTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.user_1 = User.objects.create_user(username='Mike1')
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

        self.user_2 = User.objects.create_user(username='Mike2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

        self.test_group = Group.objects.create(
            title="Тестова группа",
            slug="slag",
            description="Тестовое описание"
        )
        self.test_post = Post.objects.create(
            text="Тестовый пост",
            author=self.user_1,
            group=self.test_group
        )

    def test_urls_allowed_guests(self):
        """Страницы c доступом для неавторизованного пользователя"""
        urls = [
            '',
            '/about/author/',
            '/about/tech/',
            f'/{self.user_1}/{self.test_post.id}/',
            f'/group/{self.test_group.slug}/',
            f'/{self.user_1}/',
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_forbidden_guests(self):
        """Страницы без доступа для неавторизованного пользователя"""
        urls = [
            '/new/',
            f'/{self.user_1}/{self.test_post.id}/edit/',
            '/follow/',
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                redir = f'/auth/login/?next={url}'
                self.assertRedirects(response, redir)

    def test_urls_allowed_for_users(self):
        """Страницы для авторизованного пользователя."""
        urls = [
            '/new/',
            f'/{self.user_1}/{self.test_post.id}/edit/',
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_1.get(url)
                self.assertEqual(response.status_code, 200)

    def test_url_forbidden_for_another_users(self):
        """Редирект если пользователь не автор поста"""
        url = f'/{self.user_1}/{self.test_post.id}/edit/'
        response = self.authorized_client_2.get(url, follow=True)
        redir = f'/{self.user_1}/{self.test_post.id}/'
        self.assertRedirects(response, redir)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            "group.html": f'/group/{self.test_group.slug}/',
            'profile.html': f'/{self.user_1}/',
            'post.html': f'/{self.user_1}/{self.test_post.id}/',
            'new_post.html': f'/{self.user_1}/{self.test_post.id}/edit/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_incorrect_url(self):
        url = "/random/"
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_follow(self):
        """Проверяем, что страница работает"""
        response = self.authorized_client_1.get('/follow/')
        self.assertEqual(response.status_code, 200)

    def test_profile_follow(self):
        """Проверяем , что редирект при подписке верный"""
        url = f'/{self.user_1}/follow/'
        response = self.authorized_client_2.get(url, follow=True)
        redir = f'/{self.user_1}/'
        self.assertRedirects(response, redir)

    def test_profile_unfollow(self):
        """Проверяем, что при отписке редирект и данные на стр верные"""
        self.authorized_client_2.post(
            reverse('profile_follow', args=[self.user_1]))
        response1 = self.authorized_client_2.get(reverse('follow_index'))
        count_posts = len(response1.context['page'])
        self.assertEqual(count_posts, 1)

        url = f'/{self.user_1}/unfollow/'
        response2 = self.authorized_client_2.get(url, follow=True)
        redir = f'/{self.user_1}/'
        self.assertRedirects(response2, redir)

        response3 = self.authorized_client_2.get(reverse('follow_index'))
        count_posts2 = len(response3.context['page'])
        self.assertEqual(count_posts2, 0)

    def test_url_comment(self):
        """Проверяем редирект"""
        url = f'/{self.user_1}/{self.test_post.id}/comment'
        response = self.authorized_client_2.get(url, follow=True)
        redir = f'/{self.user_1}/{self.test_post.id}/'
        self.assertRedirects(response, redir)
