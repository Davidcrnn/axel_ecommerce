from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from .views import HomePage, ProductListView, ProductDetailView

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<slug>', ProductDetailView.as_view(), name='product-detail'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
