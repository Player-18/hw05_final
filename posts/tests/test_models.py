from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()
        cls.author = User.objects.create(username="testuser")

        cls.group = Group.objects.create(
            title='название группы',
            slug='Слаг',
            description='описание группы'
        )

        Post.objects.create(
            text='тестовый текст',
            author=cls.author,
            group=cls.group
        )
        cls.post = Post.objects.get(
            text='тестовый текст'
        )

    def test_post_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите текст'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild_post(self):
        post = PostModelTest.post
        post_object_name = post.text
        self.assertEqual(post_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='название группы',
            slug='Слаг',
            description='описание группы'
        )

    def test_group_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Наименование группы'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild_group(self):
        group = GroupModelTest.group
        post_object_name = group.title
        self.assertEqual(post_object_name, str(group))
