from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse

from .models import Item, List


class HomePage(View):
    def get(self, request):
        return render(request, 'home.html')


class ListsView(View):
    def get(self, request, pk):
        list_ = List.objects.get(pk=pk)
        items = Item.objects.filter(list_fk=list_)
        ctx = {'items': items}
        return render(request, 'list.html', ctx)


class NewListsView(View):
    def post(self, request):
        list_ = List.objects.create()
        Item.objects.create(text=request.POST['item_text'], list_fk=list_)
        return redirect('/lists/%d' % (list_.id))
