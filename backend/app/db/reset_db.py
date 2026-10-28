from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.attribute import AtributoMencionado
from app.models.sentiment import SentimientoPlatillo
from app.models.establishment_sentiment import SentimientoEstablecimiento
from app.models.audio_transcription import TranscripcionAudio
from app.models.review import Resena
from app.models.order import Pedido, ItemPedido
from app.models.dish import Platillo
from app.db.seed import seed_dishes

def clean_and_reset_db(db: Session):
    """
    Elimina todas las reseñas, transcripciones, sentimientos (platillos y establecimiento)
    y pedidos previos dejando la base de datos limpia y asegurando que el catálogo
    de platillos esté intacto.
    """
    init_db()
    print("[Reset DB] Limpiando tablas de reseñas, sentimientos, atributos y pedidos...")
    num_attrs = db.query(AtributoMencionado).delete()
    num_sents = db.query(SentimientoPlatillo).delete()
    num_est_sents = db.query(SentimientoEstablecimiento).delete()
    num_trans = db.query(TranscripcionAudio).delete()
    num_revs = db.query(Resena).delete()
    num_order_items = db.query(ItemPedido).delete()
    num_orders = db.query(Pedido).delete()
    db.commit()

    print(
        f"[Reset DB] Eliminados: {num_revs} reseñas, {num_trans} transcripciones, "
        f"{num_sents} sentimientos platillo, {num_est_sents} sentimientos establecimiento, "
        f"{num_attrs} atributos, {num_orders} pedidos ({num_order_items} items)."
    )

    # Asegurar que los platillos del catálogo existan
    platillos_insertados = seed_dishes(db)
    total_platillos = db.query(Platillo).count()
    print(f"[Reset DB] Catálogo verificado: {total_platillos} platillos disponibles ({len(platillos_insertados)} reinsertados si faltaban).")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        clean_and_reset_db(db)
    finally:
        db.close()
