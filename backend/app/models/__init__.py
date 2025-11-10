# models package - import models so SQLAlchemy metadata knows about them
from app.models import room  # noqa: F401
from app.models import device  # noqa: F401
from app.models import agent  # noqa: F401
from app.models import decision_log  # noqa: F401
from app.models import slo  # noqa: F401
from app.models import scenario  # noqa: F401
from app.models import user  # noqa: F401