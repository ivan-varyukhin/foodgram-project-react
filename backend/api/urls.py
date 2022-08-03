from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import ProductViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', ProductViewSet)
router_v1.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
]
