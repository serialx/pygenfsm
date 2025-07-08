"""Example: Payment processing with events carrying transaction data."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto

from pygenfsm import FSM


# Payment states
class PaymentState(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    REFUNDED = auto()


# Payment events with data
@dataclass
class InitiatePaymentEvent:
    """Start a new payment."""

    amount: Decimal
    currency: str
    customer_id: str
    payment_method: str


@dataclass
class PaymentAuthorizedEvent:
    """Payment was authorized by payment provider."""

    authorization_code: str
    provider_transaction_id: str


@dataclass
class PaymentCompletedEvent:
    """Payment was successfully completed."""

    transaction_id: str
    processed_at: datetime


@dataclass
class PaymentFailedEvent:
    """Payment failed."""

    error_code: str
    error_message: str
    can_retry: bool = False


@dataclass
class RefundRequestEvent:
    """Request to refund the payment."""

    reason: str
    amount: Decimal | None = None  # None means full refund


# Payment data
@dataclass
class PaymentContext:
    amount: Decimal | None = None
    currency: str | None = None
    customer_id: str | None = None
    transaction_id: str | None = None
    authorization_code: str | None = None
    error_message: str | None = None
    refund_amount: Decimal | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


# Union type for all payment events
PaymentEvent = (
    InitiatePaymentEvent
    | PaymentAuthorizedEvent
    | PaymentCompletedEvent
    | PaymentFailedEvent
    | RefundRequestEvent
)

# Type alias
PaymentFSM = FSM[PaymentState, PaymentEvent, PaymentContext]

# Create FSM
payment = PaymentFSM(
    state=PaymentState.PENDING,
    context=PaymentContext(),
)


# Handlers
@payment.on(PaymentState.PENDING, InitiatePaymentEvent)
def initiate_payment(fsm: PaymentFSM, event: InitiatePaymentEvent) -> PaymentState:
    print(f"💳 Initiating payment of {event.amount} {event.currency}")
    print(f"   Customer: {event.customer_id}")
    print(f"   Method: {event.payment_method}")

    fsm.context.amount = event.amount
    fsm.context.currency = event.currency
    fsm.context.customer_id = event.customer_id

    return PaymentState.PROCESSING


@payment.on(PaymentState.PROCESSING, PaymentAuthorizedEvent)
def payment_authorized(fsm: PaymentFSM, event: PaymentAuthorizedEvent) -> PaymentState:
    print("✅ Payment authorized!")
    print(f"   Auth code: {event.authorization_code}")

    fsm.context.authorization_code = event.authorization_code

    # In real world, we'd capture the payment here
    # For demo, we'll auto-complete it
    return PaymentState.PROCESSING


@payment.on(PaymentState.PROCESSING, PaymentCompletedEvent)
def payment_completed(fsm: PaymentFSM, event: PaymentCompletedEvent) -> PaymentState:
    print("🎉 Payment completed successfully!")
    print(f"   Transaction ID: {event.transaction_id}")
    print(f"   Amount: {fsm.context.amount} {fsm.context.currency}")

    fsm.context.transaction_id = event.transaction_id

    return PaymentState.COMPLETED


@payment.on(PaymentState.PROCESSING, PaymentFailedEvent)
def payment_failed(fsm: PaymentFSM, event: PaymentFailedEvent) -> PaymentState:
    print("❌ Payment failed!")
    print(f"   Error: [{event.error_code}] {event.error_message}")

    fsm.context.error_message = event.error_message

    if event.can_retry:
        print("   ⚡ Payment can be retried")
        return PaymentState.PENDING
    else:
        return PaymentState.FAILED


@payment.on(PaymentState.COMPLETED, RefundRequestEvent)
def process_refund(fsm: PaymentFSM, event: RefundRequestEvent) -> PaymentState:
    refund_amount = event.amount or fsm.context.amount
    print(f"💸 Processing refund of {refund_amount} {fsm.context.currency}")
    print(f"   Reason: {event.reason}")

    fsm.context.refund_amount = refund_amount

    return PaymentState.REFUNDED


@payment.on(PaymentState.FAILED, RefundRequestEvent)
def cannot_refund_failed(fsm: PaymentFSM, event: RefundRequestEvent) -> PaymentState:
    print("⚠️  Cannot refund a failed payment")
    return PaymentState.FAILED


# Demo
async def main():
    print("=== Payment Processing FSM Demo ===\n")

    # Successful payment flow
    print("--- Successful Payment ---")
    await payment.send(
        InitiatePaymentEvent(
            amount=Decimal("99.99"),
            currency="USD",
            customer_id="cust_123",
            payment_method="credit_card",
        )
    )

    await payment.send(
        PaymentAuthorizedEvent(
            authorization_code="AUTH_789", provider_transaction_id="stripe_xyz"
        )
    )

    await payment.send(
        PaymentCompletedEvent(transaction_id="TXN_456", processed_at=datetime.now())
    )

    # Refund
    print("\n--- Refund Request ---")
    await payment.send(
        RefundRequestEvent(
            reason="Customer request",
            amount=Decimal("50.00"),  # Partial refund
        )
    )

    print(f"\nFinal state: {payment.state.name}")
    print(f"Transaction ID: {payment.context.transaction_id}")


if __name__ == "__main__":
    asyncio.run(main())
