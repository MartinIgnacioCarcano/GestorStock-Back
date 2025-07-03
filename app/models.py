from app import db, bcrypt
from datetime import datetime

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    descripcion = db.Column(db.String(200))
    stock = db.Column(db.Integer)
    stock_minimo = db.Column(db.Integer)
    proveedor = db.Column(db.String(100))
    categoria = db.Column(db.String(50))
    estado = db.Column(db.String(30))
    
    def actualizar_estado(self):
        if self.stock<=0:
            self.estado = 'Sin Stock'
        elif self.stock<=self.stock_minimo:
            self.estado = 'Bajo Stock'
        else:
            self.estado = 'En Stock'
    
class Extraccion(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    descripcion = db.Column(db.String(200))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    detalles = db.relationship(
        'DetalleExtraccion', 
        backref='extraccion', 
        cascade="all, delete-orphan"  # Elimina detalles al borrar la extracción
    )

class DetalleExtraccion(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    extraccion_id = db.Column(db.Integer, db.ForeignKey('extraccion.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    cantidad = db.Column(db.Integer)
    producto = db.relationship('Producto', backref='detalles_extraccion')

class Ingreso(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    detalles = db.relationship("DetalleIngreso", backref="ingreso", cascade="all, delete-orphan")

class DetalleIngreso(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ingreso_id = db.Column(db.Integer, db.ForeignKey('ingreso.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    cantidad = db.Column(db.Integer)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }
