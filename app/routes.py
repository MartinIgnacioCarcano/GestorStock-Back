from flask import Blueprint, request, jsonify,Response
from app import db
from app.models import Producto, Extraccion, DetalleExtraccion, Usuario,Ingreso, DetalleIngreso
from datetime import datetime
import time
import json
import jwt
import os
from flask_jwt_extended import verify_jwt_in_request,create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from flask import current_app

SECRET_KEY = "tu_clave_secreta_aqui"  

productos_bp = Blueprint('productos', __name__)
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios():
    try:
        usuarios = Usuario.query.all()
        print(f"Usuarios encontrados: {len(usuarios)}")
        return jsonify([{
            "id": u.id,
            "username": u.username
        } for u in usuarios])
    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        return jsonify({"error": "Hubo un error al obtener los usuarios"}), 500

@auth_bp.route("/rr", methods=["POST"])
@jwt_required()
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    usuario_id = get_jwt_identity()
    if usuario_id != 1:
        return jsonify({"error": "No tienes permiso para registrar usuarios"}), 403
    else:
        if Usuario.query.filter_by(username=username).first():
            return jsonify({"error": "Usuario ya existe"}), 400

        nuevo_usuario = Usuario(username=username)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({"message": "Usuario registrado con éxito"})

@auth_bp.route('/login', methods=['POST','OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Esta respuesta explícita es CLAVE para evitar el error
        response = current_app.make_default_options_response()
        return response
    
    data = request.get_json()
    userName = data.get("username")
    password = data.get("password")
    print(f"Intento de login: {userName}")
    print(f"Password: {password}")
    if not userName or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    user = Usuario.query.filter_by(username=userName).first()

    if not user or not user.check_password(password):  # Cambiar si usás hash
        return jsonify({"error": "Credenciales incorrectas"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token), 200


    # usuario = Usuario.query.get(id)
    # if not usuario:
    #     return jsonify({"error": "Usuario no encontrado"}), 404
    # try:
    #     db.session.delete(usuario)
    #     db.session.commit()
    #     return jsonify({"mensaje": f"Usuario ID {id} eliminado"}), 200
    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({"error": str(e)}), 500

@auth_bp.route('/islogged', methods=['GET'])
@jwt_required()
def protegido():
    usuario_id = get_jwt_identity()
    return jsonify({"mensaje": f"Acceso concedido al usuario {usuario_id}"})


@auth_bp.route('/cambiar-password', methods=['PUT'])
def cambiar_password_dev():
    data = request.get_json()
    usuario_id = data.get("id")
    nueva_password = data.get("password")

    if not usuario_id or not nueva_password:
        return jsonify({"error": "Faltan datos"}), 400

    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    usuario.set_password(nueva_password)
    db.session.commit()

    return jsonify({"message": f"Contraseña actualizada para usuario ID {usuario_id}"}), 200
#--------------------------
# Rutas para Productos ----
#--------------------------
@productos_bp.route('/productos', methods=['GET'])
@jwt_required()
def get_productos():
    productos = Producto.query.all()
    print(f"Productos encontrados: {len(productos)}")
    return jsonify([{
        "id": p.id,
        "descripcion": p.descripcion,
        "stock": p.stock,
        "stock_minimo": p.stock_minimo,
        "proveedor": p.proveedor,
        "categoria": p.categoria,
        "estado": p.estado
    } for p in productos])

@productos_bp.route('/productos', methods=['POST'])
@jwt_required()
def crear_producto():
    try:
        data = request.get_json()
        nuevo_producto = Producto(
            descripcion=data['descripcion'],
            stock=int(data['stock']),
            stock_minimo=int(data['stock_minimo']),
            proveedor=data.get('proveedor', ''),
            categoria=data.get('categoria', 'General')
        )
        nuevo_producto.actualizar_estado()
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Producto creado exitosamente",
            "id": nuevo_producto.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Error al crear producto: {str(e)}",
            "tipo_error": type(e).__name__
        }), 500

@productos_bp.route('/productos/<int:id>', methods=['PATCH'])
@jwt_required()
def modificar_producto(id):
    data = request.json
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({
            "error": f"No se encontró el producto"
        }), 404
    try:
        # Actualizar solo los campos proporcionados
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'stock' in data:
            producto.stock = data['stock']
            producto.actualizar_estado()
        if 'stock_minimo' in data:
            producto.stock_minimo = data['stock_minimo']
            producto.actualizar_estado()
        if 'proveedor' in data:
            producto.proveedor = data['proveedor']
        if 'categoria' in data:
            producto.categoria = data['categoria']
        if 'estado' in data:
            producto.estado = data['estado']
        
        db.session.commit()
        return jsonify({
            "mensaje": "Producto actualizado correctamente",
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
   
@productos_bp.route('/productos/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({
            "error": f"No se encontró el producto"
        }), 404
    try:
        db.session.delete(producto)
        db.session.commit()
        return jsonify({
            "mensaje": "Producto eliminado correctamente",
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
   
#-----------------------------
# Rutas para Extracciones ----
#-----------------------------
@productos_bp.route('/extracciones', methods=['GET'])
@jwt_required()
def listar_extracciones():
    extracciones = Extraccion.query.all()
    data = []
    
    for e in extracciones:
        detalles = []
        for d in e.detalles:
            detalles.append({
                "producto_id": d.producto_id,  # Orden explícito
                "cantidad": d.cantidad
            })
        
        data.append({
            "id": e.id,
            "descripcion": e.descripcion,
            "fecha": e.fecha.isoformat(),
            "usuario_id": e.usuario_id,
            "detalles": detalles
        })
    
    # Serialización manual controlando el orden
    json_str = json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False)
    return Response(json_str, mimetype='application/json')

@productos_bp.route('/extracciones', methods=['POST'])
@jwt_required()
def crear_extraccion():
    data = request.json
    
    # Validación básica
    if not data or 'productos' not in data:
        return jsonify({"error": "Formato inválido. Se requiere 'productos' como lista"}), 400
    
    try:
        # 1. Validar stock antes de cualquier operación
        productos_con_error = []
        for item in data["productos"]:
            producto = Producto.query.get(item["producto_id"])
            if not producto:
                productos_con_error.append(f"Producto ID {item['producto_id']} no existe")
                continue
            if producto.stock < item["cantidad"]:
                productos_con_error.append(
                    f"Stock insuficiente para {producto.descripcion} (Stock actual: {producto.stock}, Se requieren: {item['cantidad']})"
                )
        
        if productos_con_error:
            return jsonify({"error": "Validación fallida", "detalles": productos_con_error}), 400
        
        # 2. Crear la extracción si todo está OK
        nueva_extraccion = Extraccion(
            usuario_id= get_jwt_identity(),  # ID de usuario temporal
            descripcion=data.get('descripcion', 'Extracción sin descripción'),
            fecha= datetime.fromisoformat(data.get('fecha')) if data.get('fecha') else datetime.now()
        )
        db.session.add(nueva_extraccion)
        db.session.flush()  # Para obtener el ID

        # 3. Procesar productos y actualizar stock
        for item in data["productos"]:
            producto = Producto.query.get(item["producto_id"])
            
            # Actualizar stock (ya validado)
            producto.stock -= item["cantidad"]
            producto.actualizar_estado()
            # Registrar detalle
            detalle = DetalleExtraccion(
                extraccion_id=nueva_extraccion.id,
                producto_id=producto.id,
                cantidad=item["cantidad"]
            )
            db.session.add(detalle)
        
        db.session.commit()
         
        return jsonify({
            "mensaje": "Extracción registrada exitosamente",
            "extraccion_id": nueva_extraccion.descripcion,
            "stock_actualizado": [{
                "producto_id": item["producto_id"],
                "nuevo_stock": Producto.query.get(item["producto_id"]).stock
            } for item in data["productos"]]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
      
@productos_bp.route('/extracciones/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_extraccion(id):
    try:
        data = request.get_json(silent=True) or {}
        devolver = data.get('devolver', 0)
        
        extraccion = Extraccion.query.get(id)
        if not extraccion:
            return jsonify({"error": f"No se encontró ninguna extracción con ID {id}"}), 404

        # Restaurar stock si corresponde
        if devolver == 1:
            for detalle in extraccion.detalles:
                producto = Producto.query.get(detalle.producto_id)
                if producto:
                    producto.stock += detalle.cantidad
                    producto.actualizar_estado()

        # Eliminar detalles y extracción

        db.session.delete(extraccion)
        
        db.session.commit()
        
        return jsonify({
            "mensaje": f"Extracción ID {id} eliminada",
            "stock_restaurado": devolver == 1,
            "detalles_eliminados": True
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar la extracción: {str(e)}"}), 500
    
#------------------------
#Rutas para Ingresos ----
#------------------------
@productos_bp.route("/ingresos", methods=["GET"])
@jwt_required()
def listar_ingresos():
    ingresos = Ingreso.query.all()
    resultado = []
    for ingreso in ingresos:
        detalles = [{
            "producto_id": d.producto_id,
            "cantidad": d.cantidad
        } for d in ingreso.detalles]
        resultado.append({
            "id": ingreso.id,
            "fecha": ingreso.fecha,
            "usuario_id": ingreso.usuario_id,
            "detalles": detalles
        })
    return jsonify(resultado)

@productos_bp.route("/ingresos", methods=["POST"])
@jwt_required()
def registrar_ingreso():
    from datetime import datetime
    data = request.get_json()

    # Validación mínima
    if not data or "detalles" not in data:
        return jsonify({"error": "Formato inválido. Se requiere 'detalles' como lista"}), 400

    fecha_str = data.get("fecha")
    if fecha_str:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
    else:
        fecha = datetime.utcnow()
    
    try:
        nuevo_ingreso = Ingreso(
            usuario_id=get_jwt_identity(),  # temporal, mientras es pública
            fecha=fecha
        )
        db.session.add(nuevo_ingreso)
        db.session.flush()  # para obtener el ID antes de los detalles

        resumen_stock = []

        for item in data["detalles"]:
            producto = Producto.query.get(item["producto_id"])
            if not producto:
                continue  # Ignorar productos inexistentes, o podés retornar error

            producto.stock += item["cantidad"]
            producto.actualizar_estado()

            detalle = DetalleIngreso(
                ingreso_id=nuevo_ingreso.id,
                producto_id=producto.id,
                cantidad=item["cantidad"]
            )
            db.session.add(detalle)

            resumen_stock.append({
                "producto_id": producto.id,
                "nuevo_stock": producto.stock
            })

        db.session.commit()

        return jsonify({
            "mensaje": "Ingreso registrado exitosamente",
            "ingreso_id": nuevo_ingreso.id,
            "stock_actualizado": resumen_stock
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@productos_bp.route('/ingresos/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_ingreso(id):
    try:
        data = request.get_json(silent=True) or {}
        devolver = data.get('devolver', 0)

        ingreso = Ingreso.query.get(id)
        if not ingreso:
            return jsonify({"error": f"No se encontró el ingreso con ID {id}"}), 404

        # Revertir stock solo si devolver == 1
        if devolver == 1:
            for detalle in ingreso.detalles:
                producto = Producto.query.get(detalle.producto_id)
                if producto:
                    print(f"Revirtiendo stock de {producto.descripcion}: {producto.stock} -> {producto.stock} - {detalle.cantidad}")
                    producto.stock -= detalle.cantidad
                    producto.actualizar_estado()

        db.session.delete(ingreso)
        db.session.commit()

        return jsonify({
            "mensaje": f"Ingreso ID {id} eliminado",
            "stock_revertido": devolver == 1,
            "detalles_eliminados": True
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

