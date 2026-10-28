from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.dish import Platillo
from app.models.order import Pedido, ItemPedido
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse

router = APIRouter()

def _build_order_response(pedido: Pedido) -> OrderResponse:
    items_resp: List[OrderItemResponse] = []
    for it in pedido.items:
        nombre = it.platillo.nombre if it.platillo else "Platillo eliminado"
        categoria = it.platillo.categoria if it.platillo else "General"
        subtotal = round(it.cantidad * it.precio_unitario, 2)
        items_resp.append(
            OrderItemResponse(
                id=it.id,
                platillo_id=it.platillo_id,
                platillo_nombre=nombre,
                platillo_categoria=categoria,
                cantidad=it.cantidad,
                precio_unitario=it.precio_unitario,
                subtotal=subtotal
            )
        )
    return OrderResponse(
        id=pedido.id,
        qr_token=pedido.qr_token,
        mesa=pedido.mesa,
        total=round(pedido.total, 2),
        estado=pedido.estado,
        created_at=pedido.created_at,
        items=items_resp,
        total_resenas=len(pedido.resenas) if pedido.resenas is not None else 0
    )

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo pedido y generar token QR")
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Registra una comanda tomada por el mesero con sus platillos y cantidades,
    genera un identificador único `qr_token` para la mesa y devuelve el detalle del pedido.
    """
    platillo_ids = [item.platillo_id for item in payload.items]
    platillos_db = db.query(Platillo).filter(Platillo.id.in_(platillo_ids)).all()
    mapa_platillos = {p.id: p for p in platillos_db}

    for item in payload.items:
        if item.platillo_id not in mapa_platillos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platillo con ID '{item.platillo_id}' no encontrado en el catálogo."
            )

    nuevo_pedido = Pedido(
        mesa=payload.mesa or "Mesa General",
        total=0.0,
        estado="CREADO"
    )
    db.add(nuevo_pedido)
    db.flush()

    total_calculado = 0.0
    for item in payload.items:
        platillo = mapa_platillos[item.platillo_id]
        subtotal = platillo.precio * item.cantidad
        total_calculado += subtotal
        nuevo_item = ItemPedido(
            pedido_id=nuevo_pedido.id,
            platillo_id=platillo.id,
            cantidad=item.cantidad,
            precio_unitario=platillo.precio
        )
        db.add(nuevo_item)

    nuevo_pedido.total = round(total_calculado, 2)
    db.commit()

    pedido_completo = db.query(Pedido).options(
        joinedload(Pedido.items).joinedload(ItemPedido.platillo),
        joinedload(Pedido.resenas)
    ).filter(Pedido.id == nuevo_pedido.id).first()

    return _build_order_response(pedido_completo)

@router.get("", response_model=List[OrderResponse], summary="Listar pedidos recientes")
def list_orders(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Retorna la lista de pedidos más recientes con sus platillos y conteo de reseñas."""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.items).joinedload(ItemPedido.platillo),
        joinedload(Pedido.resenas)
    ).order_by(Pedido.created_at.desc()).limit(limit).all()

    return [_build_order_response(p) for p in pedidos]

@router.get("/by-token/{qr_token}", response_model=OrderResponse, summary="Consultar pedido por token QR")
def get_order_by_token(
    qr_token: str,
    db: Session = Depends(get_db)
):
    """
    Busca un pedido a partir de su `qr_token` único al escanear el código QR en mesa.
    Permite que múltiples comensales de la misma mesa consulten y evalúen el pedido.
    """
    pedido = db.query(Pedido).options(
        joinedload(Pedido.items).joinedload(ItemPedido.platillo),
        joinedload(Pedido.resenas)
    ).filter(Pedido.qr_token == qr_token).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún pedido asociado al código QR '{qr_token}'."
        )

    return _build_order_response(pedido)
