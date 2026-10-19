from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from .forms import ContactForm
from .models import BlogPost, ContactMessage, Project, ProjectImage, Testimonial
from .utils import calculate_age, is_bot, should_count_view


class ContactFormTests(SimpleTestCase):
    """آزمون اعتبارسنجی فرم تماس."""

    def valid_data(self, **overrides):
        data = {
            "name": "Ramtin",
            "email": "ramtin@example.com",
            "subject": "Test subject",
            "message": "This is a valid test message.",
            "website": "",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = ContactForm(data=self.valid_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_message_is_stripped(self):
        form = ContactForm(
            data=self.valid_data(message="   This is a valid message.   ")
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["message"], "This is a valid message.")

    def test_message_shorter_than_ten_characters_is_invalid(self):
        form = ContactForm(data=self.valid_data(message="Too short"))

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_message_longer_than_three_thousand_characters_is_invalid(self):
        form = ContactForm(data=self.valid_data(message="x" * 3001))

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_message_with_exactly_ten_characters_is_valid(self):
        form = ContactForm(data=self.valid_data(message="1234567890"))

        self.assertTrue(form.is_valid(), form.errors)

    def test_message_with_exactly_three_thousand_characters_is_valid(self):
        form = ContactForm(data=self.valid_data(message="x" * 3000))

        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_email_is_rejected(self):
        form = ContactForm(data=self.valid_data(email="not-an-email"))

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_honeypot_field_is_optional(self):
        form = ContactForm(data=self.valid_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_honeypot_is_not_a_model_field(self):
        self.assertNotIn(
            "website", [field.name for field in ContactMessage._meta.fields]
        )


class ModelTests(TestCase):
    """آزمون مدل‌ها و رفتارهای پایه."""

    def test_project_string_representation(self):
        project = Project(
            title="Portfolio Project",
            category="web_design",
            image="projects/test.png",
        )

        self.assertEqual(str(project), "Portfolio Project")

    def test_project_image_string_representation(self):
        project = Project.objects.create(
            title="Portfolio Project",
            category="web_design",
            image="projects/test.png",
        )
        project_image = ProjectImage.objects.create(
            project=project,
            image="projects/extra.png",
            order=1,
        )

        self.assertEqual(str(project_image), "Portfolio Project - 1")

    def test_project_images_are_ordered(self):
        project = Project.objects.create(
            title="Portfolio Project",
            category="web_design",
            image="projects/test.png",
        )
        later_image = ProjectImage.objects.create(
            project=project,
            image="projects/later.png",
            order=2,
        )
        earlier_image = ProjectImage.objects.create(
            project=project,
            image="projects/earlier.png",
            order=1,
        )

        images = list(project.extra_images.all())

        self.assertEqual(images, [earlier_image, later_image])

    def test_deleting_project_deletes_extra_images(self):
        project = Project.objects.create(
            title="Portfolio Project",
            category="web_design",
            image="projects/test.png",
        )
        ProjectImage.objects.create(
            project=project,
            image="projects/extra.png",
        )

        project.delete()

        self.assertEqual(ProjectImage.objects.count(), 0)

    def test_testimonial_defaults(self):
        testimonial = Testimonial.objects.create(
            name="Test User",
            role="Developer",
            comment="Great work!",
        )

        self.assertEqual(testimonial.status, "pending")
        self.assertEqual(testimonial.rating, 5)
        self.assertEqual(str(testimonial), "Test User")

    def test_testimonial_rating_must_be_between_one_and_five(self):
        testimonial = Testimonial(
            name="Test User",
            role="Developer",
            comment="Great work!",
            rating=6,
        )

        with self.assertRaises(ValidationError):
            testimonial.full_clean()

    def test_blog_post_defaults(self):
        post = BlogPost.objects.create(
            title="Test Article",
            slug="test-article",
            content="Article content",
            image="blog/test.png",
        )

        self.assertEqual(post.status, "draft")
        self.assertEqual(post.category, "general")
        self.assertEqual(post.views, 0)
        self.assertEqual(str(post), "Test Article")

    def test_blog_post_slug_must_be_unique(self):
        BlogPost.objects.create(
            title="First Article",
            slug="same-slug",
            content="First content",
            image="blog/first.png",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BlogPost.objects.create(
                title="Second Article",
                slug="same-slug",
                content="Second content",
                image="blog/second.png",
            )


class HomeViewTests(TestCase):
    """آزمون صفحه اصلی و فرم تماس."""

    def setUp(self):
        self.url = reverse("home")

    def valid_contact_data(self, **overrides):
        data = {
            "name": "Ramtin",
            "email": "ramtin@example.com",
            "subject": "Test subject",
            "message": "This is a valid test message.",
            "website": "",
        }
        data.update(overrides)
        return data

    def test_home_page_returns_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertIn("form", response.context)

    def test_only_approved_testimonials_are_in_context(self):
        approved = Testimonial.objects.create(
            name="Approved User",
            role="Developer",
            comment="Approved feedback",
            status="approved",
        )
        Testimonial.objects.create(
            name="Pending User",
            role="Developer",
            comment="Pending feedback",
            status="pending",
        )

        response = self.client.get(self.url)

        testimonials = list(response.context["testimonials"])
        self.assertEqual(testimonials, [approved])

    def test_only_published_blog_posts_are_in_context(self):
        published = BlogPost.objects.create(
            title="Published Article",
            slug="published-article",
            content="Published content",
            image="blog/published.png",
            status="published",
        )
        BlogPost.objects.create(
            title="Draft Article",
            slug="draft-article",
            content="Draft content",
            image="blog/draft.png",
            status="draft",
        )

        response = self.client.get(self.url)

        blogs = list(response.context["blogs"])
        self.assertEqual(blogs, [published])

    def test_valid_contact_form_saves_message(self):
        response = self.client.post(
            self.url,
            self.valid_contact_data(),
        )

        self.assertRedirects(response, self.url)
        self.assertEqual(ContactMessage.objects.count(), 1)

        message = ContactMessage.objects.get()
        self.assertEqual(message.name, "Ramtin")
        self.assertEqual(message.email, "ramtin@example.com")
        self.assertEqual(message.message, "This is a valid test message.")

    def test_filled_honeypot_does_not_save_message(self):
        response = self.client.post(
            self.url,
            self.valid_contact_data(website="I am a bot"),
        )

        self.assertRedirects(response, self.url)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_invalid_contact_form_does_not_save_message(self):
        response = self.client.post(
            self.url,
            self.valid_contact_data(message="short"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertIn("message", response.context["form"].errors)

    @patch("main.views.time.time", return_value=1000)
    def test_contact_form_throttling_blocks_rapid_submission(self, mocked_time):
        self.client.post(self.url, self.valid_contact_data())

        with patch("main.views.time.time", return_value=1010):
            response = self.client.post(
                self.url,
                self.valid_contact_data(
                    email="another@example.com",
                    subject="Second message",
                ),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)


class BlogDetailViewTests(TestCase):
    """آزمون نمایش مقاله و شمارش بازدید."""

    def setUp(self):
        self.post = BlogPost.objects.create(
            title="Test Article",
            slug="test-article",
            content="This is **important** content.",
            image="blog/test.png",
            status="published",
        )
        self.url = reverse("blog_detail", kwargs={"slug": self.post.slug})
        self.browser_headers = {"HTTP_USER_AGENT": "Mozilla/5.0 Test Browser"}

    def test_published_article_is_displayed(self):
        response = self.client.get(self.url, **self.browser_headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "detail.html")
        self.assertContains(response, "Test Article")
        self.assertContains(response, "<strong>important</strong>", html=False)

    def test_draft_article_returns_404(self):
        self.post.status = "draft"
        self.post.save(update_fields=["status"])

        response = self.client.get(self.url, **self.browser_headers)

        self.assertEqual(response.status_code, 404)

    def test_unknown_article_returns_404(self):
        response = self.client.get(
            reverse("blog_detail", kwargs={"slug": "missing-article"}),
            **self.browser_headers,
        )

        self.assertEqual(response.status_code, 404)

    def test_first_human_visit_increments_views(self):
        self.client.get(self.url, **self.browser_headers)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

    def test_same_session_does_not_count_same_article_twice(self):
        self.client.get(self.url, **self.browser_headers)
        self.client.get(self.url, **self.browser_headers)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

    def test_bot_visit_does_not_increment_views(self):
        self.client.get(
            self.url,
            HTTP_USER_AGENT="Googlebot",
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 0)

    def test_staff_visit_does_not_increment_views(self):
        user = get_user_model().objects.create_user(
            username="staff-test",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(user)

        self.client.get(self.url, **self.browser_headers)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 0)


class UtilityTests(SimpleTestCase):
    """آزمون توابع کمکی."""

    def test_calculate_age_before_birthday(self):
        self.assertEqual(
            calculate_age(date(2000, 10, 20), date(2026, 10, 19)),
            25,
        )

    def test_calculate_age_on_birthday(self):
        self.assertEqual(
            calculate_age(date(2000, 10, 19), date(2026, 10, 19)),
            26,
        )

    def test_empty_user_agent_is_considered_bot(self):
        request = RequestFactory().get("/")
        request.user = AnonymousUser()

        self.assertTrue(is_bot(request))

    def test_bot_user_agent_is_detected(self):
        request = RequestFactory().get(
            "/",
            HTTP_USER_AGENT="Googlebot",
        )
        request.user = AnonymousUser()

        self.assertTrue(is_bot(request))

    def test_normal_browser_is_not_considered_bot(self):
        request = RequestFactory().get(
            "/",
            HTTP_USER_AGENT="Mozilla/5.0 Test Browser",
        )
        request.user = AnonymousUser()

        self.assertFalse(is_bot(request))

    def test_non_get_request_does_not_count_view(self):
        request = RequestFactory().post(
            "/",
            HTTP_USER_AGENT="Mozilla/5.0 Test Browser",
        )
        request.user = AnonymousUser()
        request.session = {}

        self.assertFalse(should_count_view(request, 123))
        self.assertEqual(request.session, {})

    def test_already_seen_article_is_not_counted_again(self):
        request = RequestFactory().get(
            "/",
            HTTP_USER_AGENT="Mozilla/5.0 Test Browser",
        )
        request.user = AnonymousUser()
        request.session = {"viewed_posts": [123]}

        self.assertFalse(should_count_view(request, 123))

    def test_first_visit_is_counted_and_recorded_in_session(self):
        request = RequestFactory().get(
            "/",
            HTTP_USER_AGENT="Mozilla/5.0 Test Browser",
        )
        request.user = AnonymousUser()
        request.session = {"viewed_posts": []}

        self.assertTrue(should_count_view(request, 123))
        self.assertIn(123, request.session["viewed_posts"])
