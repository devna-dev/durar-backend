import json

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Payment
from .permissions import CanManagePayments
from .serializers import PaymentSerializer, PaymentCreditCardSerializer
from ..points.services import PointsService
from ..points.models import UserStatistics
from ..users.services import FCMService


class PaymentsViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (CanManagePayments,)

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentSerializer
        if self.action == 'create':
            return PaymentCreditCardSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Payment.objects.filter(user_id=self.request.user.id)
        return Payment.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(context={'request': request}, data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            if not data or str(data.status).lower() == 'failed':
                return Response(data.payment_response['Message'], status=status.HTTP_400_BAD_REQUEST)

        return Response(True, status=status.HTTP_201_CREATED)

    @action(detail=True, name='payment-success', permission_classes=[AllowAny])
    def success(self, request, pk=None, *args, **kwargs):
        payment = Payment.objects.filter(pk=pk)
        if payment:
            payment.update(status='success')
            UserStatistics.objects.donation(payment.user)
            FCMService.notify_payment_success(payment.user)
            PointsService().donation_award(payment.user, payment)
        return Response(1)

    @action(detail=True, name='payment-error', permission_classes=[AllowAny])
    def error(self, request, pk=None, *args, **kwargs):
        payment = Payment.objects.filter(pk=pk)
        if payment:
            payment.update(status='fail', payment_response=json.dumps(request.data))
            FCMService.notify_payment_rejected(payment.user)
        return Response(1)
