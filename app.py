from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Conexión a la base de datos
server = 'DESKTOP-T3R6SRM\SQLEXPRESS'
database = 'Inventarios'
driver = '{SQL Server}'
conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database}"
connection = pyodbc.connect(conn_str)

# Ruta para registrar un nuevo producto
@app.route("/productos", methods=["POST"])
def registrar_producto():
    nuevo_producto = request.get_json()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Productos (Id, Nombre, Descripcion, Precio, Cantidad) VALUES (?, ?, ?, ?, ?)",
                   nuevo_producto["id"], nuevo_producto["nombre"], nuevo_producto["descripcion"],
                   nuevo_producto["precio"], nuevo_producto["cantidad"])
    connection.commit()
    return jsonify({"message": "Producto registrado exitosamente."})

# Ruta para obtener un producto por su ID
@app.route("/productos/<int:producto_id>", methods=["GET"])
def obtener_producto(producto_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Productos WHERE Id = ?", producto_id)
    producto = cursor.fetchone()
    if producto:
        producto_dict = {
            "id": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio": float(producto[3]),
            "cantidad": producto[4]
        }
        return jsonify(producto_dict)
    return jsonify({"message": "Producto no encontrado."}), 404

# Ruta para actualizar la información de un producto
@app.route("/productos/<int:producto_id>", methods=["PUT"])
def actualizar_producto(producto_id):
    datos_actualizados = request.get_json()
    cursor = connection.cursor()
    cursor.execute("UPDATE Productos SET Nombre = ?, Descripcion = ?, Precio = ?, Cantidad = ? WHERE Id = ?",
                   datos_actualizados["nombre"], datos_actualizados["descripcion"], datos_actualizados["precio"],
                   datos_actualizados["cantidad"], producto_id)
    connection.commit()
    return jsonify({"message": "Producto actualizado exitosamente."})

# Ruta para registrar una venta y actualizar las existencias del producto
@app.route("/ventas", methods=["POST"])
def registrar_venta():
    venta = request.get_json()
    cursor = connection.cursor()
    cursor.execute("SELECT Cantidad FROM Productos WHERE Id = ?", venta["producto_id"])
    cantidad_actual = cursor.fetchone()[0]
    if cantidad_actual >= venta["cantidad"]:
        cursor.execute("INSERT INTO Ventas (Id, ProductoId, Cantidad, FechaVenta) VALUES (?, ?, ?, GETDATE())",
                       venta["id"], venta["producto_id"], venta["cantidad"])
        cursor.execute("UPDATE Productos SET Cantidad = Cantidad - ? WHERE Id = ?", venta["cantidad"], venta["producto_id"])
        connection.commit()
        return jsonify({"message": "Venta registrada exitosamente."})
    else:
        return jsonify({"message": "No hay suficientes existencias del producto."}), 400

# Ruta para obtener un reporte de todos los productos y los datos relacionados a ellos
@app.route("/reporte", methods=["GET"])
def obtener_reporte():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Productos")
    productos = []
    for producto in cursor.fetchall():
        producto_dict = {
            "id": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio": float(producto[3]),
            "cantidad": producto[4]
        }
        productos.append(producto_dict)
    return jsonify(productos)

if __name__ == "__main__":
    app.run(port=5001)

