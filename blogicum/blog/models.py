from django.db import models
from django.contrib.auth import get_user_model

from core.models import BaseModel

User = get_user_model()
MAX_LENGTH = 256


class Location(BaseModel):
    name = models.CharField(
        verbose_name='Название места',
        max_length=MAX_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Category(BaseModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=MAX_LENGTH)
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL;'
                  ' разрешены символы латиницы,'
                  ' цифры, дефис и подчёркивание.')
    description = models.TextField(
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Post(BaseModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        verbose_name='Заголовок', max_length=MAX_LENGTH)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
                  '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор публикации',
        related_name='posts',
        on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Местоположение',
        null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Категория',
        null=True)
    image = models.ImageField('Фото', upload_to='posts_images',
                              blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['pub_date']


class Comment(BaseModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария', null=True)
    text = models.TextField(verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
