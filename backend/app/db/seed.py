from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.dish import Platillo

SEED_DISHES = [
    {
        "nombre": "Tacos de Res Braseada",
        "categoria": "Tacos / Fuertes",
        "precio": 195.0,
        "descripcion": "Tres tacos con res braseada a fuego lento en tortilla artesanal con cebolla curtida y salsa martajada.",
        "activo": True
    },
    {
        "nombre": "Ribeye a la Parrilla",
        "categoria": "Cortes",
        "precio": 480.0,
        "descripcion": "Corte selecto de 350g asado a las brasas de encino con papas al romero y chiles toreados.",
        "activo": True
    },
    {
        "nombre": "Sopa Azteca",
        "categoria": "Entradas / Sopas",
        "precio": 110.0,
        "descripcion": "Sopa tradicional de tortilla frita con aguacate, queso fresco, crema y tiras de chile pasilla.",
        "activo": True
    },
    {
        "nombre": "Guacamole Rústico",
        "categoria": "Entradas",
        "precio": 135.0,
        "descripcion": "Aguacate Hass machacado con pico de gallo fresco, cilantro y totopos de maíz azul horneados.",
        "activo": True
    },
    {
        "nombre": "Salmón al Ajillo",
        "categoria": "Pescados / Fuertes",
        "precio": 340.0,
        "descripcion": "Filete de salmón fresco sellado con finas láminas de ajo frito, chile guajillo y arroz salvaje.",
        "activo": True
    },
    {
        "nombre": "Pastel Tres Leches",
        "categoria": "Postres",
        "precio": 95.0,
        "descripcion": "Bizcocho esponjoso bañado en salsa tradicional de tres leches con toque de canela y fresas frescas.",
        "activo": True
    },
    {
        "nombre": "Agua de Horchata Artesanal",
        "categoria": "Bebidas",
        "precio": 45.0,
        "descripcion": "Bebida fresca artesanal de arroz, canela criolla y toque de vainilla.",
        "activo": True
    }
]

def seed_dishes(db: Session) -> list[Platillo]:
    """Inserta los platillos iniciales si no existen en la base de datos."""
    creados = []
    for dish_data in SEED_DISHES:
        existente = db.query(Platillo).filter(Platillo.nombre == dish_data["nombre"]).first()
        if not existente:
            nuevo = Platillo(**dish_data)
            db.add(nuevo)
            creados.append(nuevo)
    
    if creados:
        db.commit()
        for p in creados:
            db.refresh(p)
    return creados

if __name__ == "__main__":
    print("Inicializando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        insertados = seed_dishes(db)
        print(f"Seed completado exitosamente: {len(insertados)} platillos nuevos insertados.")
        total = db.query(Platillo).count()
        print(f"Total de platillos en el catálogo: {total}")
    finally:
        db.close()
