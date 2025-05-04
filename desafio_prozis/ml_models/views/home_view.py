from django.shortcuts import render


def home_view(request):
    context = {
        "username": request.user.username if request.user.is_authenticated else "",
    }
    return render(request, "home/home_page.html", context)
