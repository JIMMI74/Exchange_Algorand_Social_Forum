from django.urls import path
from . import views
from accounts.views import SocialPage

urlpatterns = [
    path("new-section/", views.CreateSection.as_view(), name="create_section"),
    path("section/<int:pk>/", views.section_view, name="section_view"),
    path("section/<int:pk>/crea-discussione/", views.create_discussion, name="create_discussion"),
    path("discussion/<int:pk>/", views.discussion_view, name="discussion_view"),
    path("discussion/<int:pk>/ansewer/", views.add_request, name="request_discussion"),
    path("discussion/<int:id>/delete_post/<int:pk>/", views.DeletePost.as_view(), name="delete_post"),
    path("socialpage", SocialPage.as_view(), name="social_page"),
]
