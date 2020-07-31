"""Tests template tags."""

from django.test import TestCase

from forecasts.templatetags.sigdig import sigdig


class SigDigTest(TestCase):
    def test_sig_dig(self):
        self.assertEqual(sigdig(99), '99.0')
        self.assertEqual(sigdig(999.9), '1000')
        self.assertEqual(sigdig(123.45, 4), '123.5')
        self.assertEqual(sigdig(123.45, 1), '100')
        self.assertEqual(sigdig('foo'), 'foo')
