from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .forms import PersonForm, PersonModelForm
from django.db.models import Q
from .models import Person, MyStock
from .forms import StockFilterForm
from django.views.generic import View
from django.views.generic import FormView, CreateView, DetailView, ListView, UpdateView

def extendtest(request):
    return render(request, 'ex_form/base.html')


class Myview7(UpdateView):
    model = Person
    form_class = PersonModelForm
    # template_name = 'ex_form/person_form'
    success_url = '/ex/exam09'

class Myview6(ListView):
    model = Person
    


class Myview5(DetailView):
    model = Person
    # template_name= 'ex_form/person_detail.html'  ## app/ model명 _ detail.html



class Myview4(CreateView):
    model = Person
    form_class = PersonModelForm
    template_name = 'ex_form/exam05_form.html'
    success_url = '/ex/'



class Myview3(FormView):
    form_class = PersonModelForm
    template_name = 'ex_form/exam05_form.html'
    success_url = '/ex/'

    def form_valid(self, form):
        print('데이터가 유효하면')
        m = Person(**form.cleaned_data)
        m.save()
        return super().form_valid(form)

class Myview2(View):
    form_class = PersonForm
    initial = {
        'name':'이름',
        'age':0
    }
    template_name = 'ex_form/exam05_form.html'
    
    def get(self, request):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form':form})
    
    
    def post(self, request):
        form = PersonModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ex_form:index')
    
        return render(request, 'ex_form/exam04_form.html', {'form':form})

class Myview1(View):
    
    def get(self, request):
        form = PersonModelForm()
        return render(request, 'ex_form/exam04_form.html', {'form':form})
    
    def post(self, request):
        form = PersonModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ex_form:index')
    
        return render(request, 'ex_form/exam04_form.html', {'form':form})
            

# Create your views here.
def index(request):
    return render(request, 'ex_form/index.html')

def exam01(request):
    print('exam01')
    if request.method == "POST":
        name = request.POST['name']
        age = request.POST['age']
        print('요청 처리', name, age)
        Person(name=name, age=age).save()
        return HttpResponse('처리완료')
    else:
        return render(request, 'ex_form/exam01_form.html')


def exam02(request):
    print('exam02')
    if request.method == 'POST':
        personForm = PersonForm(request.POST)
        if personForm.is_valid(): # 유효성을 검증 
            name = personForm.cleaned_data['name']
            age = personForm.cleaned_data['age']
            Person(name=name, age=age).save()
            return HttpResponse('처리완료')
        else:
            return render(
                request,
                'ex_form/exam02_form.html',
                {'form': personForm}
            )
    else:
        form = PersonForm()
        print(form)
        return render(request, 'ex_form/exam02_form.html', {'form':form})




from .forms import PersonModelForm
def exam03(request):
    print('exam03')
    if request.method == 'POST':
         form = PersonModelForm(request.POST)
         if form.is_valid():
            form.save()
            return HttpResponse('처리완료')

    else:
        form = PersonModelForm()
    
    return render(request, 'ex_form/exam03_form.html', {'form':form})


def stock_list(request):
    
    category_filters = []
    mystocks = MyStock.objects.all()
    if request.method == 'POST':
        form = StockFilterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('new_bra'):
                category_filters.append('new_bra')
            if form.cleaned_data.get('3w'):
                category_filters.append('3w')
            if form.cleaned_data.get('sun'):
                category_filters.append('sun')
            if form.cleaned_data.get('consen'):
                category_filters.append('consen')
            
            if category_filters:
                query = Q()
                for category in category_filters:
                    query &= Q(reasons__icontains=category)
                mystocks = mystocks.filter(query)
                print('필터되서 rendering!!')
            else:
                print('전체데이터')
            return render(request, "ex_form/stock_list.html", {"form":form, 'mystocks':mystocks})
                
        else:
            print('is_valid failed! ')
            return render(request, "ex_form/stock_list.html", {"form":form, 'mystocks':mystocks})
    else:
        form = StockFilterForm()
        print('그냥 rendering!!')
        print("category_filters",category_filters)
        return render(request, "ex_form/stock_list.html", {"form":form, 'mystocks':mystocks}) 
    