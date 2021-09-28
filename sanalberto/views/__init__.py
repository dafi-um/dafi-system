from .activities import (
    ActivitiesIndexView,
    ActivityDetailView,
    ActivityRegisterView,
    ActivityRegistrationsView,
    RegistrationDetailView,
    RegistrationListView,
    RegistrationPaidView,
    RegistrationUpdateView,
)
from .main import (
    IndexView,
    InfoView,
)
from .polls import (
    DesignCreateView,
    PollIndexView,
)
from .shop import (
    ShopClosedView,
    ShopIndexView,
)


__all__ = [
    "ActivitiesIndexView",
    "ActivityDetailView",
    "ActivityRegisterView",
    "ActivityRegistrationsView",
    "DesignCreateView",
    "IndexView",
    "InfoView",
    "PollIndexView",
    "RegistrationDetailView",
    "RegistrationListView",
    "RegistrationPaidView",
    "RegistrationUpdateView",
    "ShopClosedView",
    "ShopIndexView",
]
