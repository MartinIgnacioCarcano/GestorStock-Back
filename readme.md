# GestorStock - Backend

Este es el backend de **GestorStock**, una aplicación web pensada para pymes que necesitan llevar el control de stock de forma colaborativa y segura.

El sistema permite que múltiples empleados realicen ingresos y extracciones de productos, y que el administrador pueda visualizar qué hizo cada usuario. Toda la lógica de autenticación, gestión de datos y trazabilidad está implementada aquí.

---

## ⚙️ Tecnologías utilizadas

- **Python + Flask** – Framework backend
- **PostgreSQL** – Base de datos relacional (almacenada en Supabase)
- **SQLAlchemy** – ORM para manejar la base de datos
- **bcrypt** – Encriptación de contraseñas
- **JWT (JSON Web Tokens)** – Autenticación de usuarios
- **CORS** – Para integración frontend-backend

---

## 🔒 Seguridad

- Las contraseñas se almacenan en forma encriptada con `bcrypt`.
- Los tokens JWT aseguran las rutas privadas.
- Se valida que cada acción (ingreso/extracción) quede registrada bajo el usuario que la realizó.

---

## 🌍 Producción

- Backend desplegado en Render: [https://gestorstock-back.onrender.com](https://gestorstock-back.onrender.com)

⚠️ Render puede tardar **1 a 2 minutos** en levantar el servidor si está inactivo. Esto puede afectar la primera carga al iniciar sesión desde el frontend.

---
