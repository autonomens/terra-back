from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feature, FeatureRelation, Layer, LayerRelation
from .serializers import (FeatureRelationSerializer, FeatureSerializer,
                          LayerRelationSerializer, LayerSerializer,
                          TerraUserSerializer)


class LayerViewSet(viewsets.ModelViewSet):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer

    @detail_route(methods=['get'], url_path='geojson')
    def to_geojson(self, request, pk=None):
        layer = self.get_object()
        return Response(layer.to_geojson())


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    swagger_schema = None  # FIXME: Temporary disable schema generation


class LayerRelationViewSet(viewsets.ModelViewSet):
    queryset = LayerRelation.objects.all()
    serializer_class = LayerRelationSerializer


class FeatureRelationViewSet(viewsets.ModelViewSet):
    queryset = FeatureRelation.objects.all()
    serializer_class = FeatureRelationSerializer
    swagger_schema = None  # FIXME: Temporary disable schema generation


class UserInformationsView(APIView):
    def get(self, request):
        user = self.request.user
        return Response(TerraUserSerializer(user).data)


class SettingsView(APIView):
    def get(self, request):
        terra_settings = {
            'statuses': dict(settings.STATUSES.VALUE_TO_CONST),
        }

        return Response(terra_settings)
