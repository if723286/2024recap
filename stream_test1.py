import streamlit as st
import pandas as pd
import random
import urllib.parse
import datetime

def asignar_tasa_interes(monto_prestamo, periodos, primera_vez):
    if primera_vez:
        if periodos <= 6:
            return random.uniform(7.0, 7.6)
        else:
            return random.uniform(7.7, 8.3)
    else:
        # Monto de 2,000
        if monto_prestamo <= 200 and periodos <= 6:
            return random.uniform(6.5, 6.7)
        elif monto_prestamo <= 200 and periodos <= 12:
            return random.uniform(6.8, 7.0)
        # Monto de 4,000
        elif monto_prestamo <= 400 and periodos <= 6:
            return random.uniform(6.0, 6.2)
        elif monto_prestamo <= 400 and periodos <= 12:
            return random.uniform(6.3, 6.5)
        # Monto de 6,000
        elif monto_prestamo <= 600 and periodos <= 6:
            return random.uniform(5.5, 5.7)
        elif monto_prestamo <= 600 and periodos <= 12:
            return random.uniform(5.8, 6.0)
        # Monto de 8,000
        elif monto_prestamo <= 800 and periodos <= 6:
            return random.uniform(5.0, 5.2)
        elif monto_prestamo <= 800 and periodos <= 12:
            return random.uniform(5.3, 5.5)
        # Monto de 10,000
        elif monto_prestamo <= 1000 and periodos <= 6:
            return random.uniform(4.5, 4.7)
        else:
            return random.uniform(4.7, 5)


def calcular_tabla_amortizacion(monto_prestamo, periodos, primera_vez):
    tasa_interes = asignar_tasa_interes(monto_prestamo, periodos, primera_vez)
    tasa_interes_mensual = tasa_interes / 100
    pago_mensual = monto_prestamo * (tasa_interes_mensual / (1 - (1 + tasa_interes_mensual) ** -periodos))

    fecha_actual = datetime.date.today()
    fecha_inicio = fecha_actual + datetime.timedelta(days=30)  # Agrega un mes

    saldo_restante = monto_prestamo
    tabla_amortizacion = []

    for i in range(1, periodos + 1):
        pago_interes = saldo_restante * tasa_interes_mensual
        pago_principal = pago_mensual - pago_interes
        saldo_restante -= pago_principal

        fecha_pago = fecha_inicio + datetime.timedelta(days=(i - 1) * 30)  # Agrega 30 días por cada período
        tabla_amortizacion.append((i, fecha_pago, monto_prestamo, pago_principal, pago_interes, saldo_restante))

    return tabla_amortizacion, tasa_interes


def mostrar_tabla_amortizacion(tabla_amortizacion, fecha_inicio):
    df = pd.DataFrame(tabla_amortizacion, columns=["Número de Pago", "Fecha de Pago", "Principal", "Interés", "Pago total", "Saldo restante"])
    df["Fecha de Pago"] = pd.date_range(start=fecha_inicio, periods=len(df), freq="M")
    df["Fecha de Pago"] = df["Fecha de Pago"].dt.strftime("%Y-%m-%d")
    df["Principal"] = df["Principal"].map("${:,.2f}".format)
    df["Interés"] = df["Interés"].map("${:,.2f}".format)
    df["Pago total"] = df["Pago total"].map("${:,.2f}".format)
    df["Saldo restante"] = df["Saldo restante"].map("${:,.2f}".format)
    df = df.reset_index(drop=True)  # Reiniciar el índice y convertirlo en una columna regular
    st.table(df)


def enviar_por_correo(monto_prestamo, tasa_interes, total_intereses, total_pagos):
    email = "admon@moonetaes.com"
    subject = "Información de préstamo"
    body = f"Aquí está la información de mi préstamo:\n" \
           f" \n" \
           f"Monto de préstamo: ${monto_prestamo:,.2f}\n" \
           f"Tasa de interés asignada: {tasa_interes:.2f}%\n" \
           f"Total de intereses pagados: ${total_intereses:,.2f}\n" \
           f"Total de pagos realizados: ${total_pagos:,.2f}"

    mailto_url = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    st.write(f"Esta es solo una simulación del préstamo que podrías obtener. Para obtener más información, haz clic en el siguiente enlace:")
    st.write(f"[Enviar información por correo electrónico]({mailto_url})")

# Aplicación de Streamlit
st.title("Simulador de Préstamo")

fecha_inicio = st.date_input("Seleccione la fecha en la que desea adquirir el préstamo", value=(datetime.date.today() + datetime.timedelta(days=30)))
monto_prestamo = st.slider("Seleccione el monto del préstamo:", min_value=0, max_value=1_000, step=10, value=500, format="$%d")
periodos = st.slider("Seleccione Duración de préstamo (en meses):", min_value=1, max_value=12, step=1, value=6, key="periodos_slider")
primera_vez = st.radio("¿Es la primera vez que solicita un préstamo a Moonetaes?", ("Sí", "No")) == "Sí"

st.write('---')

if st.button("Calcular"):
    if primera_vez and monto_prestamo > 1000:
        st.write("Esta vez podemos prestarte hasta $1,000 pesos por ser la primera vez que solicitas un préstamo con nosotros")
        st.write("Aquí está tu tabla de pagos. ¡Sé puntual con todos los pagos y podrías obtener un monto de crédito mayor la próxima vez!")
        monto_prestamo = 1000
    
    tabla_amortizacion, tasa_interes = calcular_tabla_amortizacion(monto_prestamo, periodos, primera_vez)

    # Modificación de la columna "Monto" para mostrar el pago total (principal + interés)
    tabla_amortizacion = [(i, fecha_pago, pago_principal, pago_interes, pago_principal + pago_interes, saldo_restante) for
                          i, fecha_pago, _, pago_principal, pago_interes, saldo_restante in tabla_amortizacion]

    mostrar_tabla_amortizacion(tabla_amortizacion, fecha_inicio)

    # Resumen de la tabla de amortización
    total_intereses = sum(row[3] for row in tabla_amortizacion)
    total_pagos = sum(row[4] for row in tabla_amortizacion)
    st.info(f"**Monto de préstamo:** ${monto_prestamo:,.2f}")
    st.info(f"**Tasa de interés mensual:** {tasa_interes:.2f}%")
    st.info(f"**Total de intereses pagados:** ${total_intereses:,.2f}")
    st.info(f"**Total de pagos realizados:** ${total_pagos:,.2f}")

    enviar_por_correo(monto_prestamo, tasa_interes, total_intereses, total_pagos)