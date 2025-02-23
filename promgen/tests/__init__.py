# Copyright (c) 2017 LINE Corporation
# These sources are released under the terms of the MIT license: see LICENSE

import json
from django.urls import reverse
import yaml

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.conf import settings


class Data:
    def __init__(self, *args, test_dir=settings.BASE_DIR / "promgen" / "tests"):
        self.path = test_dir.joinpath(*args)

    def json(self):
        with self.path.open() as fp:
            return json.load(fp)

    def yaml(self):
        with self.path.open() as fp:
            return yaml.safe_load(fp)

    def raw(self):
        with self.path.open() as fp:
            return fp.read()


class PromgenTest(TestCase):
    def testAlert(self, source="alertmanager.json", data=None):
        if data is None:
            data = Data("examples", source).raw()

        return self.client.post(
            reverse("alert"), data=data, content_type="application/json"
        )

    def assertRoute(self, response, view, status=200, msg=None):
        self.assertEqual(response.status_code, status, msg)
        self.assertEqual(response.resolver_match.func.__name__, view.as_view().__name__)

    def assertCount(self, model, count, msg=None):
        self.assertEqual(model.objects.count(), count, msg)

    def add_force_login(self, **kwargs):
        user = User.objects.create_user(**kwargs)
        self.client.force_login(user, "django.contrib.auth.backends.ModelBackend")
        return user

    def add_user_permissions(self, *args, user=None):
        codenames = [p.split(".")[1] for p in args]
        permissions = Permission.objects.filter(
            codename__in=codenames, content_type__app_label="promgen"
        )

        if user is None:
            user = self.user

        user.user_permissions.add(*[p for p in permissions])


SETTINGS = Data("examples", "promgen.yml").yaml()
