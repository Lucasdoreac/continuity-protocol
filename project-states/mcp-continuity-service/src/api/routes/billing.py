# Sistema de Monetização - Stripe Integration
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import stripe
import os
from typing import Dict, Any
from ..models.auth import User

# Configurar Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_stripe_key_here")

router = APIRouter(prefix="/billing", tags=["billing"])

# Função temporária para autenticação - deve ser implementada no sistema completo
async def get_current_user() -> User:
    """Placeholder para autenticação - implementar conforme necessário"""
    # Em produção, verificar token JWT aqui
    return User(
        email="user@example.com",
        username="demo_user",
        plan="free"
    )

class SubscriptionRequest(BaseModel):
    price_id: str
    payment_method_id: str

class WebhookEvent(BaseModel):
    data: Dict[Any, Any]
    type: str

# Planos de preços (configurar no Stripe Dashboard)
PRICE_IDS = {
    "pro": "price_pro_monthly_id",
    "enterprise": "price_enterprise_monthly_id"
}

@router.post("/create-subscription")
async def create_subscription(request: SubscriptionRequest, current_user = Depends(get_current_user)):
    """Criar nova assinatura"""
    try:
        # Criar customer no Stripe
        customer = stripe.Customer.create(
            email=current_user.email,
            payment_method=request.payment_method_id,
            invoice_settings={'default_payment_method': request.payment_method_id}
        )
        
        # Criar assinatura
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': request.price_id}],
            expand=['latest_invoice.payment_intent']
        )
        
        return {"subscription_id": subscription.id, "status": subscription.status}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(event: WebhookEvent):
    """Webhook para eventos do Stripe"""
    if event.type == "invoice.payment_succeeded":
        # Renovar assinatura do usuário
        customer_id = event.data["object"]["customer"]
        # Atualizar status na base de dados
        return {"status": "success"}
    
    elif event.type == "invoice.payment_failed":
        # Cancelar assinatura
        return {"status": "payment_failed"}
    
    return {"status": "ignored"}
