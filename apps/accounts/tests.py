from django.test import TestCase

# Create your tests here.
from apps.accounts.models import User

class ReviewTestCase(TestCase):
    # User = CustomUser()
    user = User


