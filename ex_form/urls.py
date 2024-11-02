from django.urls import path, include
from . import views

app_name = 'ex_form'

urlpatterns = [
    path('', view=views.index, name='index'),
    path('extendtest', view=views.extendtest, name='extendtest'),
    path('exam01/', view=views.exam01, name='exam01'),
    path('exam02/', view=views.exam02, name='exam02'),
    path('exam03/', view=views.exam03, name='exam03'),
    path('stocks/', view=views.stock_list, name='stock_list'),
    # path('', view=views.index, name='index'),
    # 클래스형 뷰
    path('exam04/', view=views.Myview1.as_view(), name='exam04'),
    path('exam05/', view=views.Myview2.as_view(), name='exam05'),
    path('exam06/', view=views.Myview3.as_view(), name='exam06'), # formview 저장하진 않아.
    path('exam07/', view=views.Myview4.as_view(), name='exam07'), # Createview
    path('exam08/<int:pk>', view=views.Myview5.as_view(), name='exam08'), # Detailview
    path('exam09/', view=views.Myview6.as_view(), name='exam09'), # Listview
    path('exam10/<int:pk>/', view=views.Myview7.as_view(), name='exam10'), # Updateview
]
