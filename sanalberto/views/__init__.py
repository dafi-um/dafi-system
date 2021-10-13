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
    'PollDetailView',
    'PollVoteCreateView',
    'RegistrationDetailView',
    'RegistrationListView',
    'RegistrationPaidView',
    'RegistrationUpdateView',
    'ShopClosedView',
    'ShopIndexView',
]
