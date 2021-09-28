from django.template import (
    Context,
    Template,
)
from django.test import TestCase


class UsersTemplateTagsTests(TestCase):

    def render_nice_name(self, user):
        template_str = '{% load users_tags %}{{ user|nice_name }}'
        context = Context({'user': user})
        return Template(template_str).render(context)

    def test_nice_name_returns_username(self):
        """nice_name tag returns the username when the full name is not available"""

        class UserNoName():
            username = 'my_username'

            def get_full_name(self):
                return None

        rendered = self.render_nice_name(UserNoName())

        self.assertEquals(rendered, 'my_username')

    def test_nice_name_returns_full_namename(self):
        """nice_name tag returns the full name when is available"""

        class User():
            username = 'my_username'

            def get_full_name(self):
                return 'my_full_name'

        rendered = self.render_nice_name(User())

        self.assertEquals(rendered, 'my_full_name')
