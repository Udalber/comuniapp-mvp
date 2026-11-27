import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parent.parent
READ_SHIPPING = (
    "import django; django.setup(); "
    "from django.conf import settings; print(settings.SHIPPING_COST)"
)


class ShippingCostSettingTests(SimpleTestCase):
    """SHIPPING_COST se lee de la variable de entorno al cargar settings."""

    def _run(self, shipping_cost=None):
        env = {**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings", "PYTHON_DOTENV_DISABLED": "1"}
        env.pop("SHIPPING_COST", None)
        if shipping_cost is not None:
            env["SHIPPING_COST"] = shipping_cost
        return subprocess.run(
            [sys.executable, "-c", READ_SHIPPING],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_default_is_8000(self):
        result = self._run()
        self.assertEqual(result.stdout.strip(), "8000")

    def test_reads_environment_variable(self):
        result = self._run("12500")
        self.assertEqual(result.stdout.strip(), "12500")

    def test_invalid_value_fails_fast(self):
        result = self._run("ocho mil")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHIPPING_COST", result.stderr)

    def test_negative_value_fails_fast(self):
        result = self._run("-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHIPPING_COST", result.stderr)
