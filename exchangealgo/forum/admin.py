from django.contrib import admin
from .models import Discussion, Post, HomepageSection


class DiscussionModelAdmin(admin.ModelAdmin):
    model = Discussion
    list_display = ["title", "membership", "author_discussion"]
    search_fields = ["title", "author_discussion"]
    list_filter = ["membership", "published"]


class PostModelAdmin(admin.ModelAdmin):
    model = Post
    list_display = ["author_post", "discussion"]
    search_fields = ["content"]
    list_filter = ["published", "author_post"]


class SectionModelAdmin(admin.ModelAdmin):
    model = HomepageSection
    list_display = ["title_section", "description"]


admin.site.register(Discussion, DiscussionModelAdmin)
admin.site.register(Post, PostModelAdmin)
admin.site.register(HomepageSection, SectionModelAdmin)

