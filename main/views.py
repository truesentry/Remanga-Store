from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Review, Favorite
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.http import JsonResponse


@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('products')
    else:
        form = ProductForm()
    return render(request, 'main/create.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'main/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'main/register.html', {
                'error': 'Такий користувач уже існує'
            })
        User.objects.create_user(username=username, password=password)
        return redirect('login')
    return render(request, 'main/register.html')


def products(request):
    all_products = Product.objects.all()

    search = request.GET.get('search', '').strip()
    if search:
        all_products = all_products.filter(name__icontains=search)

    category = request.GET.get('category')
    if category:
        all_products = all_products.filter(category=category)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            all_products = all_products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            all_products = all_products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    return render(request, 'main/products.html', {'products': all_products})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'main/profile.html')


def home(request):
    new_arrivals = Product.objects.filter(is_new=True)[:5]
    popular = Product.objects.order_by('-rating')[:5]
    manga_items = Product.objects.filter(category='manga')[:4]
    manhwa_items = Product.objects.filter(category='manhwa')[:4]
    manhua_items = Product.objects.filter(category='manhua')[:4]
    context = {
        'new_arrivals': new_arrivals,
        'popular': popular,
        'manga_items': manga_items,
        'manhwa_items': manhwa_items,
        'manhua_items': manhua_items,
    }
    return render(request, 'main/home.html', context)


def about(request):
    context = {
        'title': 'Про нас',
        'description': 'RemangaStore — найкращий магазин манги, манхви та маньхуа в Україні.'
    }
    return render(request, 'main/about.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    reviews = product.reviews.select_related('user').order_by('-created_at')
    is_favorite = False
    user_review = None
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
        user_review = reviews.filter(user=request.user).first()
    return render(request, 'main/product_detail.html', {
        'product': product,
        'related': related,
        'reviews': reviews,
        'is_favorite': is_favorite,
        'user_review': user_review,
    })


def search_autocomplete(request):
    query = request.GET.get('q', '')
    results = []
    if len(query) >= 1:
        all_products = Product.objects.all()
        query_lower = query.lower()
        matched_ids = [p.id for p in all_products if query_lower in p.name.lower()]
        prods = Product.objects.filter(id__in=matched_ids)[:8]
        results = [
            {
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'category': p.get_category_display(),
            }
            for p in prods
        ]
    return JsonResponse({'results': results})


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        text = request.POST.get('text', '').strip()
        if text:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': rating, 'text': text}
            )
    return redirect('product_detail', pk=pk)


@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        is_fav = False
    else:
        is_fav = True
    return JsonResponse({'is_favorite': is_fav})


@login_required
def favorites(request):
    fav_products = Product.objects.filter(favorited_by__user=request.user)
    return render(request, 'main/favorites.html', {'products': fav_products})
