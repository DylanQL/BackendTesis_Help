# Expose model classes defined in models.py so `import core.models` works
# Django expects the app's models module to be importable as `core.models`.
# Keep this file intentionally small to avoid import-time side effects.
from .models import *  # noqa: F401,F403
from .models_telematico import *  # noqa: F401,F403

# Note: models.py does not define __all__; we intentionally avoid importing
# it to prevent import errors. If you later add __all__ there, you can
# re-export it here for hygiene.
