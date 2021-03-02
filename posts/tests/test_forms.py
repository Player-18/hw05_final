import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import NewForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = NewForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='MikeT')
        self.user_client = Client()
        self.user_client.force_login(self.user)

        self.test_post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )
        self.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
        )

        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    def test_add_new_post(self):
        post_count = Post.objects.count()
        form = {
            'text': 'Тестовая пост2',
            'group': self.test_group.id,
        }
        self.user_client.post(
            reverse('new_post'),
            data=form,
            follow=True)

        cont = post_count + 1
        self.assertEqual(Post.objects.count(), cont)

    def test_form_edit_post(self):
        form = {
            'group': self.test_group.id,
            'text': 'new text',
        }
        response = self.user_client.post(
            reverse('post_edit', args=[self.user, self.test_post.id]),
            data=form,
            follow=True
        )
        self.test_post.refresh_from_db()
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={'username': self.user.username,
                                             'post_id': self.test_post.id}))
        self.assertEqual(self.test_post.text, form['text'])

    def test_post_and_image(self):
        form_date = {
            'text': 'Изображение',
            'image': self.uploaded
        }
        self.user_client.post(
            reverse("new_post"),
            data=form_date,
            follow=True
        )
        post = Post.objects.filter(text='Изображение').first()
        self.assertIsNotNone(post.image.url)
