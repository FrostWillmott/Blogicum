from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    # location = forms.ModelChoiceField(
    #     queryset=Location.objects.all(),
    #     empty_label='Выберите местоположение',
    #     to_field_name='name',
    #     label='Местоположение')
    # category = forms.ModelChoiceField(
    #     queryset=Category.objects.all(),
    #     empty_label='Выберите категорию',
    #     to_field_name='title',
    #     label='Категория')

    class Meta:
        model = Post
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}),
            #     'location': forms.Select(attrs={'class': 'form-control'}),
            #     'category': forms.Select(attrs={'class': 'form-control'}),
        }

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
