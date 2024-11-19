import pandas as pd

# POSICIÓN GLOBAL
# Variables globales para rastrear la posición actual en el código fuente
global line, col, stack_col

def reset_globals():
    """
    Reinicia las variables globales antes de cada análisis.
    Se utiliza para garantizar que las líneas y columnas
    comiencen desde el inicio en cada ejecución.
    """
    global line, col, stack_col
    line = 1  # Línea inicial
    col = 0   # Columna inicial
    stack_col = []  # Pila para rastrear columnas al procesar nuevas líneas

def lexical_analysis(code):
    """
    Función principal de análisis léxico.
    Procesa el código fuente carácter por carácter y genera tokens según
    las reglas definidas en la matriz del autómata.
    """
    global line, col

    # Reinicia las variables globales al inicio del análisis
    reset_globals()

    # Carga la matriz de transiciones desde un archivo Excel
    matrix = pd.read_excel('./myproject/matriz.xlsx')

    # Definición de caracteres especiales y espacios
    spaces = [' ', '\t', '\n']
    pila_comillas = []  # Pila para manejar comillas abiertas y cerradas

    # Definición del alfabeto aceptado por el autómata
    alphabet = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "_", "<", ">", "=", "!", "&", "|", "+", "-", "*", "/", "(", ")", "{", "}",
        "[", "]", "\"", ".", " ", "jmp", "tab", ";"
    ]

    result = []  # Lista para almacenar los tokens generados
    token = ""  # Acumulador para construir un token
    token_start_col = 1  # Columna donde empieza el token actual
    row = 0  # Estado inicial del autómata

    for char in code:
        # Obtiene la columna de la matriz asociada al carácter actual
        column = procesar_char(char)
        
        # Si el carácter no pertenece al alfabeto, marca un error
        if column not in alphabet:
            col_pos = token_start_col
            result.append([token, "ERROR", line, col_pos])
            break

        # Transición del autómata según el carácter y estado actual
        if isinstance(matrix[column][row], int):
            row = matrix[column][row]  # Cambia al nuevo estado

            # Manejo de comillas para cadenas
            if char == "\"":
                if not pila_comillas:
                    pila_comillas.append(char)  # Comilla de apertura
                else:
                    pila_comillas.pop()  # Comilla de cierre

            # Manejo de espacios y acumulación de tokens
            else:
                if char not in spaces:
                    if not token:
                        token_start_col = col  # Marca el inicio del token
                    token += char
                elif pila_comillas:  # Si está dentro de una cadena
                    token += char
        else:
            # Si el estado no es numérico, se genera un token
            col_pos = token_start_col
            result.append([token, matrix[column][row], line, col_pos])
            
            # Manejo de errores en el estado
            if matrix[column][row] == "er" or matrix[column][row] == "e":
                result.append([token, matrix[column][row], line, col_pos])
                break

            # Reinicia el token y el estado para procesar el siguiente
            token = ""
            row = 0

            # Manejo de caracteres no espaciales que inician un nuevo token
            if char not in spaces:
                token_start_col = col  # Marca la posición inicial del nuevo token
                token += char
                row = matrix[column][row]
                if not isinstance(matrix[column][row], int) and str(matrix[column][row]) != "er":
                    col_pos = token_start_col
                    result.append([token, matrix[column][row], line, col_pos])
                    token = ""
                    row = 0

    return result

def procesar_char(char):
    """
    Determina la columna correspondiente en la matriz para el carácter dado.
    También maneja cambios de línea y tabulaciones.
    """
    global line, col
    col += 1  # Incrementa la posición de columna
    if char.isdigit():
        column = int(char)  # Números se tratan como enteros
    else:
        column = str(char)  # Otros caracteres se tratan como cadenas

    # Manejo de caracteres especiales
    if char == "\n":
        column = "jmp"  # Marca un salto de línea
        stack_col.append(col)  # Guarda la posición de columna actual
        line += 1  # Incrementa la línea
        col = 0  # Reinicia la columna en una nueva línea
    elif char == "\t":
        column = "tab"  # Marca una tabulación
        col += 3  # Avanza la columna en 4 espacios

    return column
