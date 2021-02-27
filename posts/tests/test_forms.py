from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import Post
from posts.models import Group, User


class PostCreateFormTests(TestCase):
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
