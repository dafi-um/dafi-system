from .activities import (
    ActivitiesIndexView,
    ActivityDetailView,
    ActivityRegisterView,
    ActivityRegistrationsView,
    RegistrationDetailView,
    RegistrationListView,
    RegistrationPaidView,
    RegistrationPayView,
    RegistrationUpdateView,
)
from .main import (
    IndexView,
    InfoView,
)
from .polls import (
    DesignCreateView,
    PollAdminView,
    PollDetailView,
    PollVoteCreateView,
)
from .shop import (
    ShopClosedView,
    ShopIndexView,
)


__all__ = [
    'ActivitiesIndexView',
    'ActivityDetailView',
    'ActivityRegisterView',
    'ActivityRegistrationsView',
    'DesignCreateView',
    'IndexView',
    'InfoView',
    'PollAdminView',
    'PollDetailView',
    'PollVoteCreateView',
    'RegistrationDetailView',
    'RegistrationListView',
    'RegistrationPaidView',
    'RegistrationPayView',
    'RegistrationUpdateView',
    'ShopClosedView',
    'ShopIndexView',
]
