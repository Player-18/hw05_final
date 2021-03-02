import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User


class ViewPageContextTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    def setUp(self):
        self.guest_client = Client()

        self.user_1 = User.objects.create_user(username='user1')
        self.user_1_client = Client()
        self.user_1_client.force_login(self.user_1)

        self.user_2 = User.objects.create_user(username='user2')
        self.user_2_client = Client()
        self.user_2_client.force_login(self.user_2)

        self.test_group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        self.test_group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='slug-2',
            description='Тестовое описание 2',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )

        self.test_post = Post.objects.create(
            text='Тестовый текст',
            author=self.user_1,
            group=self.test_group_1,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_uses_correct_template(self):
        """Соответсвие вызываемых шаблонов"""
        user = self.user_1
        post_id = self.test_post.id
        templates_pages_names = {
            reverse('index'): 'index.html',
            reverse('new_post'): 'new.html',
            reverse('group_posts',
                    args=[self.test_group_1.slug]): 'group.html',
            reverse('post_edit', args=[user, post_id]): 'new_post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',

        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest():
                response = self.user_1_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.user_1_client.get(reverse('index'))
        cont = self.test_post
        self.assertEqual(response.context['page'][0], cont)

    def test_group_context(self):
        url = reverse("group_posts", args=[self.test_group_1.slug])
        response = self.user_1_client.get(url)
        cont = self.test_group_1
        self.assertEqual(response.context['group'], cont)

    def test_new_post_context(self):
        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

        response = self.user_1_client.get(reverse('new_post'))
        form = response.context['form']

        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], expected)

    def test_post_edit_context(self):
        url = reverse('post_edit', args=[self.user_1, self.test_post.id])
        response = self.user_1_client.get(url)
        form = response.context['form']

        context = {
            'post': self.test_post,
            'is_edit': True,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(response.context[value], expected)

        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], expected)

    def test_profile_context(self):
        url = reverse('profile', args=[self.user_1])
        response = self.user_1_client.get(url)

        context = {
            'author': self.user_1
        }

        for key, val in context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], val)

    def test_post_view_context(self):
        url = reverse('post', args=[self.user_1, self.test_post.id])
        response = self.user_1_client.get(url)

        context = {
            'post': self.test_post,
            'author': self.user_1
        }

        for key, val in context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], val)

    def test_group_post(self):
        response = self.user_1_client.get(
            reverse('group_posts', args=[self.test_group_1.slug]))
        cont = self.test_post
        self.assertEqual(response.context['page'][0], cont)

    def test_another_group_post(self):
        response = self.user_1_client.get(
            reverse('group_posts', args=[self.test_group_2.slug]))
        cont = self.test_post
        self.assertIsNot(cont, response.context['page'])

    def test_image_context(self):
        response = self.user_1_client.get(reverse(
            'post', args=[self.user_1, self.test_post.id]))
        image = response.context.get('post').image
        self.assertEqual(image, self.test_post.image)

    def test_cache(self):
        response1 = self.user_1_client.get(reverse('index'))
        post = Post.objects.create(author=self.user_1, text='test')
        response2 = self.user_1_client.get(reverse('index'))
        Post.objects.filter(id=post.id).delete()

        response3 = self.user_1_client.get(reverse('index'))
        self.assertEqual(response2.content, response3.content)

        cache.clear()
        response4 = self.user_1_client.get(reverse('index'))
        self.assertEqual(response1.content, response4.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='test_author'
        )
        cls.second_author = User.objects.create(
            username='test_author2'
        )
        cls.group = Group.objects.create(
            title='test_title',
            slug='test-slug',
            description='test-description'
        )
        cls.post = Post.objects.create(
            text='test-post',
            author=cls.author,
            group=cls.group
        )
        cls.second_post = Post.objects.create(
            text='test-post2',
            author=cls.second_author
        )
        cls.comment = Comment.objects.create(
            post=cls.second_post,
            author=cls.second_author,
            text="ААА"
        )

    def setUp(self):
        self.user = FollowTest.author
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.second_user = FollowTest.second_author
        self.auth_client2 = Client()
        self.auth_client2.force_login(self.second_author)

        self.guest = Client()

        cache.clear()

    def test_auth_follow(self):
        follow = Follow.objects.all()
        self.assertEqual(follow.count(), 0)

        self.auth_client.post(
            reverse('profile_follow', args=[self.second_author]))

        follow = Follow.objects.filter(
            user=self.author,
            author=self.second_author)
        self.assertEqual(follow.count(), 1)

    def test_auth_delete_follow(self):
        self.auth_client.post(
            reverse('profile_follow', args=[self.second_author]))

        follow = Follow.objects.filter(
            user=self.author,
            author=self.second_author)
        self.assertEqual(follow.count(), 1)

        self.auth_client.post(
            reverse('profile_unfollow', args=[self.second_author]))

        follow = Follow.objects.filter(
            user=self.author,
            author=self.second_author)
        self.assertEqual(follow.count(), 0)

    def test_new_recording_create_in_list_subscriber(self):
        self.auth_client.post(
            reverse('profile_follow', args=[self.second_author]))
        response = self.auth_client.get(reverse('follow_index'))
        count_posts = len(response.context['page'])
        self.assertEqual(count_posts, 1)

    def test_new_recording_dont_create_in_list_subscriber(self):
        response = self.auth_client.get(reverse('follow_index'))
        count_posts = len(response.context['page'])
        self.assertEqual(count_posts, 0)

    def test_auth_comment_posts(self):
        self.auth_client.post(
            reverse('add_comment', kwargs={'username':
                                           self.second_author.username,
                                           'post_id': self.second_post.id}))
        response = self.auth_client.get(
            f'/{self.second_author}/{self.second_post.id}/')
        count_comments = len(response.context['comments'])
        self.assertEqual(count_comments, 1)

    def test_cache(self):
        response1 = self.auth_client.get(reverse('index'))
        post = Post.objects.create(author=self.author, text='test')
        response2 = self.auth_client.get(reverse('index'))
        Post.objects.filter(id=post.id).delete()

        response3 = self.auth_client.get(reverse('index'))
        self.assertEqual(response2.content, response3.content)

        cache.clear()
        response4 = self.auth_client.get(reverse('index'))
        self.assertEqual(response1.content, response4.content)
