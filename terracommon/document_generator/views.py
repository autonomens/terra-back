import os
from datetime import date

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from jinja2 import TemplateSyntaxError
from requests.exceptions import ConnectionError, HTTPError
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from terracommon.terra.helpers import get_media_response
from terracommon.trrequests.models import UserRequest

from .helpers import DocumentGenerator
from .models import DocumentTemplate


class DocumentTemplateViewSets(viewsets.ViewSet):
    """
    pdf_creator:
    Create a new pdf document from a template link to a user request.
    """
    permission_classes = (IsAuthenticated, )

    @detail_route(methods=['get'],
                  url_name='pdf',
                  url_path='pdf/(?P<request_pk>[^/.]+)')
    def pdf_creator(self, request, pk=None, request_pk=None):
        """ Insert data from user request into a template & convert it to pdf

        <pk>: template's id
        <request_pk>: user request's id
        """

        userrequest = get_object_or_404(UserRequest, pk=request_pk)
        template = get_object_or_404(DocumentTemplate, pk=pk)

        userrequest_type = ContentType.objects.get_for_model(
                                                        userrequest)
        downloadable_properties = {
            'document': template,
            'content_type': userrequest_type,
            'object_id': userrequest.pk,
        }
        if not ((request.user.is_superuser
                 or request.user.has_perm('trrequests.can_download_all_pdf')
                or request.user.downloadabledocument_set.filter(
                    **downloadable_properties).exists())):
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            pdf_generator = DocumentGenerator(template.documenttemplate.path)
            pdf_path = pdf_generator.get_pdf(data=userrequest)
        except FileNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except (ConnectionError, HTTPError):
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except TemplateSyntaxError as e:
            print(e.lineno, e.message)
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data='malformed template'
            )
        else:
            pdf_url = os.path.join(settings.MEDIA_URL, pdf_path)

            filename = f'document_{date.today().__str__()}.pdf'
            response = get_media_response(
                request,
                {'path': pdf_path, 'url': pdf_url},
                headers={
                    'Content-Type': 'application/pdf',
                    'Content-disposition': f'attachment;filename={filename}'
                }
            )
            return response
