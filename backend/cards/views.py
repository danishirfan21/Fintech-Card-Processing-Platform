"""
API Views for the Fintech Card Processing Platform.
Following RESTful principles with proper error handling and rate limiting.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import VirtualCard, Transaction, AccountSummary
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    VirtualCardSerializer,
    VirtualCardCreateSerializer,
    TransactionSerializer,
    TransactionCreateSerializer,
    AccountSummarySerializer
)
from .services import TransactionService, CardService


class TransactionRateThrottle(UserRateThrottle):
    """Custom throttle for transaction endpoints"""
    rate = '50/hour'


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={
            201: UserSerializer(),
            400: "Bad Request - Validation Error"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new user account"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(generics.RetrieveAPIView):
    """
    API endpoint to get current authenticated user details.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VirtualCardViewSet(viewsets.ModelViewSet):
    """
    API endpoints for virtual card management.
    """
    serializer_class = VirtualCardSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return cards for the authenticated user"""
        return VirtualCard.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return VirtualCardCreateSerializer
        return VirtualCardSerializer

    @swagger_auto_schema(
        operation_description="Create a new virtual card",
        request_body=VirtualCardCreateSerializer,
        responses={
            201: VirtualCardSerializer(),
            400: "Bad Request - Validation Error"
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new virtual card"""
        serializer = VirtualCardCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            card = serializer.save()
            return Response(
                {
                    'message': 'Card created successfully',
                    'card': VirtualCardSerializer(card).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Get list of user's virtual cards",
        responses={200: VirtualCardSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all cards for the authenticated user"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get details of a specific card",
        responses={
            200: VirtualCardSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get details of a specific card"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Block a card",
        responses={
            200: VirtualCardSerializer(),
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a virtual card"""
        try:
            card = CardService.block_card(pk, request.user)
            return Response(
                {
                    'message': 'Card blocked successfully',
                    'card': VirtualCardSerializer(card).data
                },
                status=status.HTTP_200_OK
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Unblock a card",
        responses={
            200: VirtualCardSerializer(),
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Unblock a virtual card"""
        try:
            card = CardService.unblock_card(pk, request.user)
            return Response(
                {
                    'message': 'Card unblocked successfully',
                    'card': VirtualCardSerializer(card).data
                },
                status=status.HTTP_200_OK
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Get transactions for a specific card",
        responses={200: TransactionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for a card"""
        try:
            transactions = CardService.get_card_transactions(pk, request.user)
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing transactions.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return transactions for the authenticated user's cards"""
        return Transaction.objects.filter(card__user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get list of user's transactions",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by transaction status",
                type=openapi.TYPE_STRING,
                enum=['PENDING', 'COMPLETED', 'FAILED', 'REVERSED']
            ),
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Filter by transaction type",
                type=openapi.TYPE_STRING,
                enum=['CREDIT', 'DEBIT']
            )
        ],
        responses={200: TransactionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List transactions with optional filters"""
        queryset = self.get_queryset()

        # Apply filters
        transaction_status = request.query_params.get('status', None)
        transaction_type = request.query_params.get('type', None)

        if transaction_status:
            queryset = queryset.filter(status=transaction_status.upper())
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type.upper())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    operation_description="Process a new transaction (credit or debit)",
    request_body=TransactionCreateSerializer,
    responses={
        201: TransactionSerializer(),
        400: "Bad Request - Validation Error"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([TransactionRateThrottle])
def process_transaction(request):
    """
    Process a new transaction (credit or debit).
    Rate limited to prevent abuse.
    """
    serializer = TransactionCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    try:
        serializer.is_valid(raise_exception=True)

        # Process transaction using service
        transaction = TransactionService.process_transaction(
            card_id=serializer.validated_data['card_id'],
            transaction_type=serializer.validated_data['transaction_type'],
            amount=serializer.validated_data['amount'],
            description=serializer.validated_data['description']
        )

        return Response(
            {
                'message': 'Transaction processed successfully',
                'transaction': TransactionSerializer(transaction).data
            },
            status=status.HTTP_201_CREATED
        )

    except DjangoValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'An error occurred while processing the transaction'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AccountSummaryView(generics.RetrieveAPIView):
    """
    API endpoint to get account summary for the authenticated user.
    """
    serializer_class = AccountSummarySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get account summary with aggregated financial data",
        responses={200: AccountSummarySerializer()}
    )
    def get(self, request, *args, **kwargs):
        """Get account summary for current user"""
        summary, created = AccountSummary.objects.get_or_create(user=request.user)
        if created or not summary.updated_at:
            summary.update_summary()

        serializer = self.get_serializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Refresh account summary with latest data",
        responses={200: AccountSummarySerializer()}
    )
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Refresh account summary"""
        summary, _ = AccountSummary.objects.get_or_create(user=request.user)
        summary.update_summary()
        serializer = self.get_serializer(summary)
        return Response(
            {
                'message': 'Account summary refreshed successfully',
                'summary': serializer.data
            },
            status=status.HTTP_200_OK
        )
