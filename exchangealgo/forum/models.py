from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import math


class HomepageSection(models.Model):
    title_section = models.CharField(max_length=80)
    description = models.CharField(max_length=150, blank=True, null=True)
    logo_section = models.ImageField(blank=True, null=True)

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return self.title_section

    def get_absolute_url(self):
        return reverse("section_view", kwargs={"pk": self.pk})

    def get_last_discussions(self):

        return Discussion.objects.filter(membership=self).order_by("-published")[:2]

    def get_number_of_posts_in_section(self):

        return Post.objects.filter(discussion__membership=self).count()


class Discussion(models.Model):
    title = models.CharField(max_length=120)
    published = models.DateTimeField(auto_now_add=True)
    author_discussion = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussions")
    membership = models.ForeignKey(HomepageSection, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Discussion"
        verbose_name_plural = "Discussions"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("discussion_view", kwargs={"pk": self.pk})

    def get_n_pages(self):
        posts_discussion = self.post_set.count()
        n_page = math.ceil(posts_discussion / 5)
        return n_page


class Post(models.Model):
    author_post = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)

    def __str__(self):
        return self.author_post.username

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.author_post.username


