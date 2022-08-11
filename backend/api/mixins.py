from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class RetrivelistViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pass
