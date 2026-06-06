from fastapi import APIRouter, Depends
from app.schemas.reconciliation import ReconcileRequest, ComparisonResult, CombinationResult, CorrectionRequest
from app.services import reconciliation_service
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import product_service

router = APIRouter(prefix="/reconcile", tags=["Reconciliation"])

@router.post("/", response_model=list[ComparisonResult])
def reconcile_payments(payload: ReconcileRequest):
    cat_amounts = reconciliation_service.reconcile_cat_amounts(payload.cat_amounts_temp)
    results = reconciliation_service.compare_payment_amounts(payload.pos_amounts, cat_amounts)
    return results

@router.post("/corrections", response_model=list[CombinationResult])
def calculate_correction_combinations(payload: CorrectionRequest, db: Session = Depends(get_db)):
    products = product_service.fetch_all_active_products(db)
    target_amount = reconciliation_service.calculate_target_amount(payload.cancelled_amount, payload.difference, payload.mode)
    products_as_dicts = [{"id": p.id, "item_name": p.item_name, "price": p.price} for p in products]
    combinations = reconciliation_service.find_combinations(products_as_dicts, target_amount, max_items=8, max_results=3)
    formatted_combinations = reconciliation_service.format_combinations(combinations)
    return formatted_combinations