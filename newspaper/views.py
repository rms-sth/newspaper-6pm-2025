from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView, View
from newspaper.models import Category, Post, Tag
from newspaper.forms import CommentForm, ContactForm, NewsletterForm

from django.utils import timezone
from datetime import timedelta


class HomeView(ListView):
    model = Post
    template_name = "aznews/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        published_at__isnull=False, status="active"
    ).order_by("-published_at")[:5]

    # for sharing extra data to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_post"] = (
            Post.objects.filter(published_at__isnull=False, status="active")
            .order_by("-published_at", "-views_count")
            .first()
        )
        context["featured_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at", "-views_count")[1:4]

        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active", published_at__gte=one_week_ago
        ).order_by("-published_at", "-views_count")[:7]

        context["recent_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:7]
        
        context['whats_new_categories'] = Category.objects.all()[:5]
        return context


class AboutView(TemplateView):
    template_name = "aznews/about.html"


class PostListView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        return Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")


class PostByCategoryView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    # to filter data we use get_queryset method
    def get_queryset(self):
        # Post.objects.all()
        query = super().get_queryset()
        query = query.filter(
            published_at__isnull=False,
            status="active",
            category__id=self.kwargs["category_id"],
        ).order_by("-published_at")
        return query


class PostByTagView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            published_at__isnull=False,
            status="active",
            tag__id=self.kwargs["tag_id"],
        ).order_by("-published_at")
        return query


class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/detail/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(published_at__isnull=False, status="active")
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # for increasing views count
        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        # 7 => 1, 2, 3, 4, 5, 6 => 6, 5, 4, 3, 2, 1
        context["previous_post"] = (
            Post.objects.filter(
                published_at__isnull=False, status="active", id__lt=obj.id
            )
            .order_by("-id")
            .first()
        )

        # 8, 9, 10 ....
        context["next_post"] = (
            Post.objects.filter(
                published_at__isnull=False, status="active", id__gt=obj.id
            )
            .order_by("id")
            .first()
        )

        return context


class CommentView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST["post"]
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("post-detail", post_id)

        post = Post.objects.get(pk=post_id)
        return render(
            request,
            "aznews/detail/detail.html",
            {"post": post, "form": form},
        )


from django.contrib import messages


class ContactView(View):
    template_name = "aznews/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Successfully submitted your query. We will contact you soon."
            )
            return redirect("contact")
        else:
            messages.error(
                request,
                "Cannot submit your query. Please make sure all fields are valid.",
            )
            return render(
                request,
                self.template_name,
                {"form": form},
            )


from django.http import JsonResponse


class NewsletterView(View):
    def post(self, request):
        is_ajax = request.headers.get("x-requested-with")
        if is_ajax == "XMLHttpRequest":
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfully subscribed to the newsletter.",
                    },
                    status=201,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Cannot subscribe to the newsletter.",
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process. Must be an AJAX XMLHttpRequest",
                },
                status=400,
            )


from django.core.paginator import PageNotAnInteger, Paginator
from django.db.models import Q


# & => and
# | => or

class PostSearchView(View):
    template_name = "aznews/list/list.html"

    def get(self, request, *args, **kwargs):
        query = request.GET["query"]  # query=nepal search => title=nepal or content=nepal
        post_list = Post.objects.filter(
            (Q(title__icontains=query) | Q(content__icontains=query)) # NEPAL
            & Q(status="active")
            & Q(published_at__isnull=False)
        ).order_by("-published_at")
        
        # pagination start
        page = request.GET.get("page", 1)  # 2
        paginate_by = 3 
        paginator = Paginator(post_list, paginate_by)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        # pagination end

        return render(
            request,
            self.template_name,
            {"page_obj": posts, "query": query},
        )
