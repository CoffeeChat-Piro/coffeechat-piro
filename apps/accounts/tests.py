from django.test import TestCase

# Create your tests here.
from apps.accounts.models import CustomUser

class ReviewTestCase(TestCase):
    # User = CustomUser()
    user = CustomUser


