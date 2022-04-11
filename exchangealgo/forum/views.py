from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView
from .forms import DiscussionModelForm, PostModelForm
from .models import Discussion, Post, HomepageSection
from .mixins import StaffMixing
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy


class CreateSection(StaffMixing, CreateView):
    model = HomepageSection
    fields = "__all__"
    template_name = "forum/create_section.html"
    success_url = "/"


def section_view(request, pk):
    section = get_object_or_404(HomepageSection, pk=pk)
    discussions_section = Discussion.objects.filter(membership=section).order_by("-published")
    context = {"section": section, "discussions": discussions_section}
    return render(request, "forum/only_section.html", context)


@login_required
def create_discussion(request, pk):
    section = get_object_or_404(HomepageSection, pk=pk)
    if request.method == "POST":
        form = DiscussionModelForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.membership = section
            discussion.author_discussion = request.user
            discussion.save()
            first_post = Post.objects.create(
                discussion=discussion,
                author_post=request.user,
                content=form.cleaned_data["content"],
            )
            first_post.save()
            return HttpResponseRedirect(discussion.get_absolute_url())
    else:
        form = DiscussionModelForm()
    context = {"form": form, "section": section}
    return render(request, "forum/create_discussion.html", context)


def discussion_view(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    posts_discussion = Post.objects.filter(discussion=discussion)
    paginator = Paginator(posts_discussion, 10)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    form_request = PostModelForm()
    context = {
        "discussion": discussion,
        "posts_discussion": posts,
        "form_request": form_request,
    }
    return render(request, "forum/only_discussion.html", context)


@login_required
def add_request(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    if request.method == "POST":
        form = PostModelForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.discussion = discussion
            form.instance.author_post = request.user
            form.save()

            url_discussion = reverse("discussion_view", kwargs={"pk": pk})
            page_in_discussion = discussion.get_n_pages()
            if page_in_discussion > 1:
                success_url = url_discussion + "?page=" + str(page_in_discussion)
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseRedirect(url_discussion)
    else:
        return HttpResponseBadRequest()


class DeletePost(DeleteView):
    model = Post
    success_url = reverse_lazy('social_page')


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author_post_id=self.request.user.id)



