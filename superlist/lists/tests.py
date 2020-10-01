from django.urls import resolve, reverse
from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from django.template.loader import render_to_string

from .views import HomePage
from .models import Item, List
import re


def remove_csrf_tag(text):
    """Remove csrf tag from TEXT
    Resolve problem with render_to_string
    """
    return re.sub(r'<[^>]*csrfmiddlewaretoken[^>]*>', '', text)


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEquals(found.func.view_class, HomePage)

    # def test_home_page_returns_correct_html(self):
    #     request = RequestFactory().get('')
    #     response = HomePage.as_view()(request)
    #     self.assertTrue(response.content.strip().startswith(b'<html>'))
    #     self.assertIn(b'<title>Listy rzeczy do zrobienia</title>',
    #                   response.content)
    #     self.assertTrue(response.content.strip().endswith(b'</html>'))

    def test_home_page_returns_correct_html(self):
        request = RequestFactory().get('')
        response = HomePage.as_view()(request)
        except_html = render_to_string('home.html', request=request)
        except_html_without_csrf = remove_csrf_tag(except_html)
        self.assertEqual(remove_csrf_tag(response.content.decode()),
                         except_html_without_csrf)

    def test_home_page_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'Nowy element listy'
        response = HomePage.as_view()(request)

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'Nowy element listy')

    def test_home_page_redirect_after_POST(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'Nowy element listy'

        response = HomePage.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'],
                         '/lists/the-only-list-in-the-world/')

        # self.assertIn('Nowy element listy', response.content.decode())
        # expected_html = render_to_string(
        #     'home.html', {'new_item_text': 'Nowy element listy'})
        # self.assertEqual(remove_csrf_tag(response.content.decode()),
        #                  remove_csrf_tag(expected_html))

    def test_home_page_only_saves_items_when_necessary(self):
        request = HttpRequest()
        # HomePage(request)
        # response = HomePage.as_view()(request)
        self.assertEqual(Item.objects.count(), 0)


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'Absolutnie pierwszy element listy'
        first_item.list_fk = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Drugi element listy'
        second_item.list_fk = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text,
                         'Absolutnie pierwszy element listy')
        self.assertEqual(first_saved_item.list_fk, list_)
        self.assertEqual(second_saved_item.text, 'Drugi element listy')
        self.assertEqual(second_saved_item.list_fk, list_)


class LiveViewTest(TestCase):
    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list_fk=correct_list)
        Item.objects.create(text='itemey 2', list_fk=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='itemey 1 listy drugiej', list_fk=other_list)
        Item.objects.create(text='itemey 2 listy drugiej', list_fk=other_list)

        response = self.client.get('/lists/%d' % (correct_list.id))

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')

        self.assertNotContains(response, 'itemey 1 listy drugiej')
        self.assertNotContains(response, 'itemey 2 listy drugiej')

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d' % (list_.id))
        self.assertTemplateUsed(response, 'list.html')

    def test_saving_a_POST_request(self):
        self.client.post('/lists/new',
                         data={'item_text': 'Nowy element listy'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'Nowy element listy')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new',
                                    data={'item_text': 'Nowy element listy'})
        # self.assertEqual(response.status_code, 302)
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d' % (new_list.id))
