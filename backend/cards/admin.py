"""
Admin configuration for the Fintech Card Processing Platform.
"""
from django.contrib import admin
from .models import VirtualCard, Transaction, AccountSummary


@admin.register(VirtualCard)
class VirtualCardAdmin(admin.ModelAdmin):
    """Admin interface for VirtualCard model"""
    list_display = (
        'id',
        'masked_card_number',
        'card_holder_name',
        'user',
        'balance',
        'status',
        'expiry_date',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'expiry_date')
    search_fields = ('card_number', 'card_holder_name', 'user__username')
    readonly_fields = ('card_number', 'cvv', 'created_at', 'updated_at', 'masked_card_number')
    ordering = ('-created_at',)

    fieldsets = (
        ('Card Information', {
            'fields': ('user', 'card_holder_name', 'card_number', 'masked_card_number', 'cvv', 'expiry_date')
        }),
        ('Financial Details', {
            'fields': ('balance', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def masked_card_number(self, obj):
        return obj.masked_card_number
    masked_card_number.short_description = 'Card Number'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model"""
    list_display = (
        'id',
        'reference_number',
        'card',
        'transaction_type',
        'amount',
        'status',
        'created_at'
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference_number', 'card__card_number', 'description')
    readonly_fields = (
        'reference_number',
        'balance_before',
        'balance_after',
        'created_at',
        'updated_at'
    )
    ordering = ('-created_at',)

    fieldsets = (
        ('Transaction Details', {
            'fields': ('card', 'transaction_type', 'amount', 'description', 'reference_number')
        }),
        ('Status & Balance', {
            'fields': ('status', 'balance_before', 'balance_after')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AccountSummary)
class AccountSummaryAdmin(admin.ModelAdmin):
    """Admin interface for AccountSummary model"""
    list_display = (
        'id',
        'user',
        'total_balance',
        'total_cards',
        'active_cards',
        'total_transactions',
        'updated_at'
    )
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'total_balance',
        'total_cards',
        'active_cards',
        'total_transactions',
        'total_credited',
        'total_debited',
        'last_transaction_date',
        'updated_at'
    )
    ordering = ('-updated_at',)

    def has_add_permission(self, request):
        """Prevent manual creation of account summaries"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of account summaries"""
        return False
