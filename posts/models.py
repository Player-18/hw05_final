from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст', help_text='Напишите текст')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор',
                               help_text="Наименование автора")
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберете группу')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение',
                              help_text='Выберите файл изображения',)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Группа",
                             help_text="Наименование группы")
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост для комментирования',)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор',)
    text = models.TextField(verbose_name='Текст',
                            help_text='Оставьте комментарий')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания комментария',)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_followings'),
        ]
