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
from django.shortcuts import render
from django.urls import path, include
from django.views import View
from rest_framework.routers import DefaultRouter

from accounts.views import UserAPIView
from alfafood import settings

from django.conf.urls.static import static

from classes.views.attendance import AttendanceViewSet#, GradeAttendanceViewSet, StudentAttendanceViewSet
from classes.views.grade import GradeViewSet
from classes.views.student import StudentViewSet
from orders.views.cart import CartViewSet
from orders.views.menu import MenuViewSet
from orders.views.order import OrderViewSet, OrderItemViewSet
from orders.views.product import ProductViewSet

router = DefaultRouter()

router.register(r'orders', OrderViewSet, basename='Order')
router.register(r'orderitems', OrderItemViewSet)
router.register(r'products', ProductViewSet, basename='Product')

router.register(r'students', StudentViewSet, basename="Student")

# router.register('attendances/grade', GradeAttendanceViewSet)
# router.register('attendances/student', StudentAttendanceViewSet, basename='student_attendance')
router.register(r'attendances', AttendanceViewSet, basename="Attendance")
# router.register(r'attendance', AttendanceViewSet)


router.register(r'grades', GradeViewSet, basename="Grade")
router.register(r'menu', MenuViewSet, basename="Menu")

# To CART urls
router.register(r'cart', CartViewSet, basename="Cart")


class HomepageView(View):
    '''вывод данных профессий'''

    def get(self, request):
        return render(request, 'homepage.html')


urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('admin/', admin.site.urls),
    path('user/', UserAPIView.as_view()),
    path('auth/', include('accounts.urls')),
    # path('canteen/', MyOwnView.as_view())
]

urlpatterns += router.get_urls()


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
