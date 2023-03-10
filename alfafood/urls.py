"""alfafood URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from accounts.views import UserAPIView
from alfafood import settings
from classes.views import StudentViewSet, AttendanceViewSet, GradeViewSet
from orders.views import OrderViewSet, OrderItemViewSet, ProductViewSet, MyOwnView

from django.conf.urls.static import static

router = SimpleRouter()

router.register(r'orders', OrderViewSet, basename='Order')
router.register(r'orderitems', OrderItemViewSet)
router.register(r'products', ProductViewSet, basename='Product')

router.register(r'students', StudentViewSet, basename="Student")

router.register(r'attendance', AttendanceViewSet, basename="Attendance")
router.register(r'grades', GradeViewSet, basename="Grade")



urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', UserAPIView.as_view()),
    path('auth/', include('accounts.urls')),
    path('canteen/', MyOwnView.as_view())
]

urlpatterns += router.urls


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
