# Mini DBMS con Árbol B+ en Python

## Descripción

Este proyecto es un mini sistema gestor de bases de datos (DBMS) desarrollado en Python con interfaz gráfica usando PyQt6.

El programa permite:

- Crear bases de datos `.json`
- Visualizar tablas
- Insertar registros
- Editar registros
- Eliminar registros
- Buscar registros mediante índices B+
- Mantener esquemas dinámicos de tablas
- Persistencia de datos en JSON
- Uso de índices B+ para búsquedas eficientes

---

# Tecnologías utilizadas

- Python 3
- PyQt6
- JSON
- Árboles B+
- PyInstaller

---

# Requisitos mínimos

## Sistema operativo

- Windows 10 o superior

## Software necesario

Si el computador está totalmente limpio, se debe instalar:

1. Visual Studio Code
2. Python 3
3. Librerías del proyecto

---

# 1. Instalar Visual Studio Code

Descargar desde:

https://code.visualstudio.com/

Instalar normalmente.

---

# 2. Instalar Python

Descargar desde:

https://www.python.org/downloads/

## IMPORTANTE

Durante la instalación marcar:

```text
☑ Add Python to PATH
```

Esto es obligatorio.

---

# 3. Verificar instalación

Abrir terminal en Visual Studio Code y ejecutar:

```bash
python --version
```

Debe aparecer algo similar a:

```text
Python 3.12.0
```

---

# 4. Descargar el proyecto

Descomprimir el proyecto en cualquier carpeta.

Ejemplo:

```text
Documentos/proyecto_dbms/
```

---

# 5. Abrir proyecto en Visual Studio Code

En VSCode:

```text
Archivo → Abrir carpeta
```

Seleccionar la carpeta del proyecto.

---

# 6. Instalar dependencias

Abrir terminal dentro de VSCode y ejecutar:

```bash
pip install PyQt6
```

---

# 7. Ejecutar el programa

Desde la terminal:

```bash
python main.py
```

---

# Estructura del proyecto

```text
project/
│
├── main.py
│
├── gui/
│   ├── main_window.py
│   ├── schema_dialog.py
│   └── record_dialog.py
│
├── engine/
│   ├── bplustree.py
│   └── database.py
│
├── storage/
│   └── file_manager.py
│
├── databases/
│   └── *.json
│
└── assets/
```

---

# Funcionamiento del programa

## Persistencia

Las bases de datos se almacenan en archivos `.json`.

Ejemplo:

```json
[
  {
    "id": 1,
    "nombre": "Pikachu"
  }
]
```

---

# Índices B+

El programa utiliza árboles B+ para:

- búsquedas rápidas
- inserciones ordenadas
- manejo eficiente de claves
- soporte de IDs repetidas

---

# Funcionamiento del índice

El árbol almacena:

```text
ID → fila
```

Ejemplo:

```text
10 → row 0
20 → row 1
30 → row 2
```

Esto permite búsquedas en tiempo:

```text
O(log n)
```

en lugar de:

```text
O(n)
```

---

# Funcionamiento interno del Árbol B+

El Árbol B+ es una estructura de datos balanceada utilizada en sistemas gestores de bases de datos reales como SQLite, MySQL y PostgreSQL.

Su función principal en este proyecto es acelerar las búsquedas dentro de las tablas.

## Estructura del árbol

Cada nodo contiene:

- claves ordenadas
- referencias a hijos
- enlaces entre hojas

Ejemplo:

```text
          [30]
         /    \
   [10 20]  [30 40]
```

Las hojas están conectadas entre sí:

```text
[10 20] -> [30 40] -> [50 60]
```

Esto permite:

- búsquedas rápidas
- búsquedas por rango
- soporte para claves repetidas

---

# Inserción

Cuando un nodo se llena, ocurre un:

```text
split
```

Ejemplo:

Antes:

```text
[10 20 30 40]
```

Después:

```text
          [30]
         /    \
   [10 20]  [30 40]
```

---

# Búsqueda

Buscar un valor implica recorrer únicamente algunos nodos:

```text
Buscar 40:

[30]
   ↓
[30 40]
```

Esto reduce enormemente la cantidad de comparaciones necesarias.

---

# Complejidades computacionales

| Operación | Complejidad |
|---|---|
| Búsqueda | O(n log n) |
| Inserción | O(n log n) |
| Eliminación | O(n log n) |

---

# Características principales

- Interfaz gráfica completa
- Bases de datos JSON
- Índices B+
- Inserción ordenada
- Soporte para claves duplicadas
- Esquemas dinámicos
- Búsquedas eficientes
- Persistencia de datos

---

# Arquitectura del proyecto

| Componente | Función |
|---|---|
| GUI | Visualización y edición |
| JSON | Persistencia |
| B+ Tree | Indexación |
| Schema | Validación de datos |

---

# Referencias bibliográficas

- Cormen, T. H. — Introduction to Algorithms
- Silberschatz — Database System Concepts
- SQLite Documentation
- Python Documentation
- PyQt6 Documentation
- Douglas Comer — The Ubiquitous B-Tree

---

# Autores

MAX y Daid Huertas
En supervisión del ingeniero Enrique Simar

Proyecto académico desarrollado para Ciencias de la Computación I.
