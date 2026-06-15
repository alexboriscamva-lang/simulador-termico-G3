"""
SIMULADOR INTERACTIVO - CICLOS DITÉRMICO vs TRITÉRMICO
Universidad Técnica de Oruro - MEC 3338 "A"
Laboratorio Nº4 - Grupo G3
Ejecutar: streamlit run app_absorcion_G3.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador Térmico G3 - UTO",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
    border: 1px solid #378ADD;
  }
  .main-header h1 { color: #85B7EB; margin: 0; font-size: 1.6rem; }
  .main-header p  { color: #B5D4F4; margin: 0.3rem 0 0; font-size: 0.9rem; }
  .metric-card {
    background: #0f3460; border: 1px solid #378ADD;
    border-radius: 10px; padding: 1rem; text-align: center;
  }
  .metric-card .val { font-size: 2rem; font-weight: 700; color: #85B7EB; }
  .metric-card .lbl { font-size: 0.75rem; color: #B5D4F4; margin-top: 4px; }
  .section-title {
    font-size: 1.1rem; font-weight: 600; color: #378ADD;
    border-left: 4px solid #378ADD; padding-left: 10px;
    margin: 1.2rem 0 0.8rem;
  }
  .formula-box {
    background: #16213e; border: 1px solid #185FA5;
    border-radius: 8px; padding: 0.8rem 1rem;
    font-family: monospace; font-size: 0.85rem; color: #C0DD97;
    margin: 0.5rem 0;
  }
  .conclusion-box {
    background: #0a2a0a; border: 1px solid #3B6D11;
    border-radius: 8px; padding: 1rem; margin: 0.5rem 0;
  }
  .conclusion-box p { color: #C0DD97; margin: 0.3rem 0; font-size: 0.9rem; }
  .warning-box {
    background: #2a1a0a; border: 1px solid #854F0B;
    border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0;
  }
  .warning-box p { color: #FAC775; margin: 0; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🧊 Simulador de Ciclos Térmicos — Laboratorio Nº4</h1>
  <p>Universidad Técnica de Oruro · MEC 3338-A · Grupo G3 · Refrigeración y Aire Acondicionado</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — PARÁMETROS EDITABLES
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Parámetros del sistema")
st.sidebar.markdown("Cambia los valores y los resultados se actualizan automáticamente.")

st.sidebar.markdown("### 🌡️ Condiciones de operación")
T_PROD  = st.sidebar.slider("Temperatura del producto (°C)",  -10.0, 15.0,  2.0, 0.5)
HR      = st.sidebar.slider("Humedad relativa HR (%)",         60.0, 95.0, 80.0, 1.0)
T_AMB   = st.sidebar.slider("Temperatura ambiente (°C)",       20.0, 45.0, 30.0, 0.5)
Q_R     = st.sidebar.slider("Capacidad frigorífica Q_R (kW)",   5.0, 50.0, 15.0, 0.5)

st.sidebar.markdown("### ❄️ Diferencias de temperatura")
DT_EVAP = st.sidebar.slider("ΔT evaporador (de gráfica HR) (°C)", 5.0, 14.0, 7.0, 0.5,
                              help="Para HR=80% → ΔT≈7°C (leído de gráfica)")
DT_COND = st.sidebar.slider("ΔT condensador (°C)", 5.0, 20.0, 10.0, 0.5)

st.sidebar.markdown("### 🔧 Sistema ditérmico (R404A)")
eta_is  = st.sidebar.slider("Eficiencia isentrópica compresor η_is", 0.50, 0.95, 0.70, 0.01)
DT_SC   = st.sidebar.slider("Subenfriamiento condensador ΔT_SC (°C)", 0.0, 10.0, 5.0, 0.5)
f_G     = st.sidebar.slider("Factor pérd. calor compresor f_G (%)", 0.0, 20.0, 10.0, 1.0)
COP_dit_base = st.sidebar.slider("COP ditérmico (ESS/CoolPack)", 1.5, 6.0, 3.099, 0.001,
                                   help="Valor obtenido del CoolPack. Ajusta si cambiaron las condiciones.")

st.sidebar.markdown("### 🔥 Sistema tritérmico (NH₃-H₂O)")
T_GEN   = st.sidebar.slider("Temperatura generador T_GEN (°C)", 80.0, 160.0, 110.0, 1.0)
DT_INT  = st.sidebar.slider("ΔT intercambiador (°C)", 10.0, 60.0, 40.0, 1.0)
ETA_Q   = st.sidebar.slider("Eficiencia quemador η_quemador", 0.70, 0.98, 0.88, 0.01)

st.sidebar.markdown("### 💰 Tarifas energéticas (Bolivia)")
TARIFA_E = st.sidebar.slider("Tarifa electricidad (Bs/kWh)", 0.10, 2.00, 0.45, 0.05)
TARIFA_G = st.sidebar.slider("Tarifa gas natural (Bs/m³)",   0.50, 5.00, 1.15, 0.05)
HORAS    = st.sidebar.slider("Horas operación por día (h)",  1.0, 24.0, 10.0, 0.5)

# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULOS AUTOMÁTICOS
# ─────────────────────────────────────────────────────────────────────────────

# Temperaturas de operación
T_EVAP = T_PROD - DT_EVAP
T_COND = T_AMB  + DT_COND

# COP Carnot
T_L_K  = T_EVAP + 273.15
T_H_K  = T_COND + 273.15
COP_CARNOT = T_L_K / (T_H_K - T_L_K) if (T_H_K - T_L_K) > 0 else 0

# Eficiencia relativa ditérmico
eta_rel_dit = COP_dit_base / COP_CARNOT if COP_CARNOT > 0 else 0

# Potencia compresor ditérmico (Q_E / COP)
W_COMP = Q_R / COP_dit_base if COP_dit_base > 0 else 0
Q_C_dit = Q_R + W_COMP

# COP tritérmico — modelo simplificado basado en temperaturas
# COP_tri_teorico = COP_Carnot * (T_GEN_K - T_COND_K) / T_GEN_K  (Lorenz)
T_GEN_K  = T_GEN + 273.15
COP_tri_teo = COP_CARNOT * (T_GEN_K - T_H_K) / T_GEN_K if T_GEN_K > T_H_K else 0
# Factor de irreversibilidad (calibrado con valor ESS = 0.3775 a condiciones base)
FACTOR_IRR = 0.3775 / (COP_CARNOT * (383.15 - 313.15) / 383.15) if COP_CARNOT > 0 else 0.35
COP_tri = COP_tri_teo * FACTOR_IRR

# Calor generador
Q_GEN_calc = Q_R / COP_tri if COP_tri > 0 else 0

# Potencia bomba (muy pequeña, proporcional al flujo)
W_BOMBA = 0.01872 * (Q_R / 15.0)  # escala proporcional al Q_R base

# Gas natural
PC_GN = 9.72  # kWh/m³
V_GN  = Q_GEN_calc / (PC_GN * ETA_Q) if (PC_GN * ETA_Q) > 0 else 0

# ── Costos ──
C_dit_hora = W_COMP * TARIFA_E
C_dit_dia  = C_dit_hora * HORAS

C_GN_hora    = V_GN * TARIFA_G
C_bomba_hora = W_BOMBA * TARIFA_E
C_tri_hora   = C_GN_hora + C_bomba_hora
C_tri_dia    = C_tri_hora * HORAS

ahorro_dia = C_dit_dia - C_tri_dia
ahorro_pct = (ahorro_dia / C_dit_dia * 100) if C_dit_dia > 0 else 0

# ─────────────────────────────────────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Resumen",
    "❄️ Ditérmico",
    "🔥 Tritérmico",
    "📋 Tablas de estado",
    "💰 Costos",
    "📈 Gráficas"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESUMEN
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Condiciones de operación calculadas</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("T_EVAP", f"{T_EVAP:.1f} °C", delta=f"T_PROD({T_PROD}°C) - ΔT({DT_EVAP}°C)")
    with c2:
        st.metric("T_COND", f"{T_COND:.1f} °C", delta=f"T_AMB({T_AMB}°C) + ΔT({DT_COND}°C)")
    with c3:
        st.metric("COP Carnot", f"{COP_CARNOT:.4f}", delta="Referencia ideal")
    with c4:
        st.metric("Q_R requerido", f"{Q_R:.1f} kW")

    st.markdown('<div class="section-title">Comparación de sistemas</div>', unsafe_allow_html=True)

    col_dit, col_vs, col_tri = st.columns([5, 1, 5])

    with col_dit:
        st.markdown("#### ❄️ Sistema Ditérmico (R404A)")
        st.metric("COP", f"{COP_dit_base:.3f}", delta=f"η_Carnot = {eta_rel_dit*100:.1f}%")
        st.metric("Potencia compresor", f"{W_COMP:.2f} kW")
        st.metric("Calor condensador Q_C", f"{Q_C_dit:.2f} kW")
        st.metric("Costo diario", f"{C_dit_dia:.1f} Bs/día")

    with col_vs:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("### VS")

    with col_tri:
        st.markdown("#### 🔥 Sistema Tritérmico (NH₃-H₂O)")
        st.metric("COP", f"{COP_tri:.4f}", delta=f"T_GEN = {T_GEN}°C")
        st.metric("Calor generador Q_GEN", f"{Q_GEN_calc:.2f} kW")
        st.metric("Potencia bomba", f"{W_BOMBA*1000:.2f} W")
        color_delta = f"Ahorro: {ahorro_pct:.1f}%" if ahorro_dia > 0 else f"Mayor costo: {-ahorro_pct:.1f}%"
        st.metric("Costo diario", f"{C_tri_dia:.1f} Bs/día",
                  delta=color_delta, delta_color="normal" if ahorro_dia > 0 else "inverse")

    st.markdown('<div class="section-title">Fórmulas aplicadas</div>', unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(f"""
<div class="formula-box">
COP_Carnot = T_L / (T_H - T_L)
           = {T_L_K:.2f} / ({T_H_K:.2f} - {T_L_K:.2f})
           = {COP_CARNOT:.4f}

W_COMP = Q_R / COP_dit
       = {Q_R:.1f} / {COP_dit_base:.3f}
       = {W_COMP:.3f} kW
</div>""", unsafe_allow_html=True)
    with col_f2:
        st.markdown(f"""
<div class="formula-box">
COP_tri = Q_R / (Q_GEN + W_bomba)
        = {Q_R:.1f} / ({Q_GEN_calc:.2f} + {W_BOMBA:.5f})
        = {COP_tri:.4f}

V_GN = Q_GEN / (PC_GN × η_q)
     = {Q_GEN_calc:.2f} / ({PC_GN} × {ETA_Q})
     = {V_GN:.4f} m³/h
</div>""", unsafe_allow_html=True)

    if ahorro_dia > 0:
        st.success(f"✅ El sistema TRITÉRMICO ahorra **{ahorro_dia:.2f} Bs/día** ({ahorro_pct:.1f}%) respecto al ditérmico.")
    else:
        st.warning(f"⚠️ Con estos parámetros el sistema ditérmico es más económico por {-ahorro_dia:.2f} Bs/día.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — DITÉRMICO
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### ❄️ Sistema Ditérmico — R404A (Flooded Evaporator)")
    st.markdown("""
    Ciclo estándar de **compresión de vapor en una etapa** con evaporador sumergido.
    Los resultados base provienen del **CoolPack/EES** con las irreversibilidades incorporadas.
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("COP real", f"{COP_dit_base:.3f}")
    col2.metric("COP* (sin pérd.)", f"{COP_dit_base*1.009:.3f}")
    col3.metric("η_Carnot", f"{eta_rel_dit:.3f}")
    col4.metric("ṁ refrigerante", f"{0.135*(Q_R/15):.4f} kg/s")

    st.markdown('<div class="section-title">Irreversibilidades incorporadas</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        irr_data = {
            "Fuente de irreversibilidad": [
                "Compresor no isentrópico",
                "Pérdida de calor en compresor",
                "Subenfriamiento condensador",
                "Sobrecalent. no útil línea succión",
                "ΔT evaporador (prod → refrig)"
            ],
            "Valor": [
                f"η_is = {eta_is:.2f}",
                f"f_G = {f_G:.0f}%",
                f"ΔT_SC = {DT_SC:.1f}°C",
                "ΔT_noutil = 1°C",
                f"ΔT = {DT_EVAP:.1f}°C"
            ],
            "Efecto": [
                "Aumenta W_comp, reduce COP",
                "Calienta vapor descarga",
                "Mejora COP levemente",
                "No enfría el producto",
                "Reduce T_evap"
            ]
        }
        st.dataframe(pd.DataFrame(irr_data), use_container_width=True, hide_index=True)

    with col_b:
        st.markdown(f"""
<div class="formula-box">
Balance energético:
  Q_C = Q_E + W_CP
  {Q_C_dit:.2f} = {Q_R:.1f} + {W_COMP:.2f} kW ✓

Eficiencia relativa:
  η = COP_real / COP_Carnot
    = {COP_dit_base:.3f} / {COP_CARNOT:.4f}
    = {eta_rel_dit:.4f}  ({eta_rel_dit*100:.1f}% del ideal)

Temperatura de descarga aprox:
  T2,is ≈ {T_COND + 5.9:.1f} °C (compresión reversible)
  T2,w  ≈ {T_COND + 14.5:.1f} °C (compresión real)
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Puntos de estado — R404A (base ESS/CoolPack)</div>', unsafe_allow_html=True)
    estados_dit_df = pd.DataFrame({
        "Punto": [1, 2, 3, 4, 5, 6, 7, 8],
        "T [°C]": [-4.0, 51.6, 51.6, 34.6, -5.4, -5.6, -5.1, -5.1],
        "P [kPa]": [513.8, 1817.3, 1817.3, 1817.3, 513.8, 513.8, 513.8, 513.8],
        "h [kJ/kg]": [216.6, 248.9, 248.9, 104.4, 104.4, 45.1, 181.6, 215.7],
        "ρ [kg/m³]": [25.8, 89.7, 89.7, 995.5, "—", 1168.5, "—", 26.0],
        "Descripción": [
            "Entrada compresor (vapor sat.)",
            "Salida compresor (real)",
            "Entrada condensador",
            "Salida condensador (líq. sat.)",
            "Salida válv. expansión",
            "Líquido evaporador (flooded)",
            "Vapor salida evaporador",
            "Salida línea de succión"
        ]
    })
    st.dataframe(estados_dit_df, use_container_width=True, hide_index=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — TRITÉRMICO
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔥 Sistema Tritérmico — NH₃-H₂O (Absorción)")
    st.markdown("""
    El **compresor mecánico** es reemplazado por un **compresor térmico**: el ciclo opera
    entre **tres niveles de temperatura** usando calor del generador (gas natural).
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("COP tritérmico", f"{COP_tri:.4f}")
    col2.metric("Q_GEN requerido", f"{Q_GEN_calc:.2f} kW")
    col3.metric("W_BOMBA", f"{W_BOMBA*1000:.2f} W")
    col4.metric("V_GN consumido", f"{V_GN:.3f} m³/h")

    st.markdown('<div class="section-title">Niveles de temperatura del sistema</div>', unsafe_allow_html=True)
    col_temps = st.columns(3)
    with col_temps[0]:
        st.markdown(f"""
<div class="formula-box">
🧊 NIVEL FRÍO
T_EVAP = {T_EVAP:.1f} °C
P_EVAP = 354.9 kPa
Refrigeración del producto
</div>""", unsafe_allow_html=True)
    with col_temps[1]:
        st.markdown(f"""
<div class="formula-box">
🌡️ NIVEL MEDIO
T_COND = {T_COND:.1f} °C
T_ABS  = 50 °C
Condensación y absorción
</div>""", unsafe_allow_html=True)
    with col_temps[2]:
        st.markdown(f"""
<div class="formula-box">
🔥 NIVEL CALIENTE
T_GEN  = {T_GEN:.1f} °C
P_COND = 1555 kPa
Generador (gas natural)
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Fracción másica de NH₃ (x) en puntos clave</div>', unsafe_allow_html=True)
    col_x1, col_x2 = st.columns(2)
    with col_x1:
        x_data = {
            "Punto / Corriente": [
                "x₁ — Solución rica (salida absorbedor)",
                "x₄ — Solución débil (salida generador)",
                "x₉ — Vapor al condensador (casi puro NH₃)",
                "x₁₄ — Vapor evaporador"
            ],
            "x [kg NH₃/kg]": [0.4329, 0.4054, 0.9994, 1.0],
            "Estado": ["Líquido sat.", "Líquido sat.", "Vapor sat.", "Mezcla Q=0.8"]
        }
        st.dataframe(pd.DataFrame(x_data), use_container_width=True, hide_index=True)
    with col_x2:
        st.markdown(f"""
<div class="formula-box">
COP = Q_R / (Q_GEN + W_BOMBA)
    = {Q_R:.1f} / ({Q_GEN_calc:.3f} + {W_BOMBA:.5f})
    = {COP_tri:.4f}

Q_GEN = Q_R / COP
      = {Q_R:.1f} / {COP_tri:.4f}
      = {Q_GEN_calc:.3f} kW

Relación Q_GEN/Q_R = {Q_GEN_calc/Q_R:.2f}
(se necesita {Q_GEN_calc/Q_R:.2f}x más calor que frío)
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Diagrama esquemático del ciclo</div>', unsafe_allow_html=True)
    st.code(f"""
  Q_GEN = {Q_GEN_calc:.2f} kW  (Gas Natural, T={T_GEN}°C)
                    ▼
         ┌──────────────────┐
         │    GENERADOR     │←── Sol. rica (x=0.4329)
         │   T={T_GEN}°C        │
         └─────┬────────┬───┘
     sol.débil │        │ vapor NH₃ (7)
        (4)   ▼        ▼
    ┌──────────┐  ┌────────────┐
    │INTERC.   │  │RECTIFICADOR│ T=45°C
    │ ΔT={DT_INT}°C  │  └─────┬──────┘
    └──────────┘        │ vapor puro (x=0.9994)
         │              ▼
         │      ┌──────────────┐
         │      │  CONDENSADOR │ T_cond={T_COND}°C
         │      └──────┬───────┘
         │             ▼ líquido NH₃
         │      ┌──────────────┐
         │      │  V.EXPANSIÓN │ → Separador
         │      └──────────────┘
         ▼ (sol. débil)
    ┌──────────────┐
    │  ABSORBEDOR  │ T=50°C  ← vapor del evaporador
    └──────┬───────┘
           │ sol. rica (x=0.4329)
           ▼
    ┌──────────────┐
    │    BOMBA     │ W={W_BOMBA*1000:.2f} W  ← muy pequeña
    └──────────────┘
    
    EVAPORADOR FLOODED: T={T_EVAP}°C | Q_R={Q_R}kW | x_out=0.8
    CÁMARA: T_prod={T_PROD}°C | HR={HR}%
    """, language=None)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — TABLAS DE ESTADO
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📋 Tablas de puntos de estado")

    st.markdown("#### Sistema Ditérmico — R404A")
    st.dataframe(estados_dit_df, use_container_width=True, hide_index=True)

    st.markdown("#### Sistema Tritérmico — NH₃-H₂O (16 estados del ESS)")
    flujos = {1:0.2836,2:0.2836,3:0.2836,4:0.2705,5:0.2705,6:0.2705,
              7:0.01378,8:0.000680,9:0.0131,10:0.0131,11:0.0131,12:0.0131,
              13:0.01458,14:0.01458,15:0.0131,16:0.0131}
    estados_tri_raw = {
        1: (-56.57,0.4329,0,    40.0,  354.9),
        2: (-55.14,0.4329,-0.001,40.1, 1555.0),
        3: (124.4, 0.4329,-0.001,80.1, 1555.0),
        4: (219.8, 0.4054,0,    100.0, 1555.0),
        5: (37.62, 0.4054,-0.001,60.0, 1555.0),
        6: (37.62, 0.4054,0.0335,48.47,354.9),
        7: (1483.0,0.9714,1,    94.46, 1555.0),
        8: (191.0, 0.4329,0,    94.46, 1555.0),
        9: (1319.0,0.9994,1,    47.57, 1555.0),
        10:(190.5, 0.9994,0,    40.0,  1555.0),
        11:(165.8, 0.9994,-0.001,35.0, 1555.0),
        12:(165.8, 0.9994,0.1471,-4.98,354.9),
        13:(-23.28,0.9994,0,    -4.98, 354.9),
        14:(1006.0,1.0,   0.8,  -5.0,  354.9),
        15:(1311.0,0.9994,1,    14.36, 354.9),
        16:(1313.0,0.9993,1,    15.36, 354.9),
    }
    descs = {
        1:"Salida absorbedor → bomba",2:"Salida bomba → intercambiador",
        3:"Salida intercambiador → generador",4:"Salida generador (sol. débil)",
        5:"Salida intercambiador → V.exp.",6:"Salida V.exp. → absorbedor",
        7:"Salida generador → rectificador",8:"Salida rectificador → generador",
        9:"Salida rectificador → condensador",10:"Salida condensador (líq. sat.)",
        11:"Condensador subenfriado",12:"Salida V.exp. → separador",
        13:"Separador → evaporador",14:"Salida evaporador → separador",
        15:"Vapor separador → absorbedor",16:"Vapor con calor no útil",
    }
    rows = []
    for n in range(1,17):
        h,x,Q,T,P = estados_tri_raw[n]
        rows.append({"Pto":n,"T [°C]":T,"P [kPa]":P,"h [kJ/kg]":h,
                     "x [NH₃]":x,"Q [-]":Q,
                     "ṁ [kg/s]":flujos[n],"Descripción":descs[n]})
    df_tri = pd.DataFrame(rows)
    st.dataframe(df_tri, use_container_width=True, hide_index=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — COSTOS
# ═════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 💰 Análisis de costos energéticos")

    st.markdown('<div class="section-title">Sistema Ditérmico — solo electricidad</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Potencia compresor", f"{W_COMP:.3f} kW")
    col2.metric("Costo por hora",     f"{C_dit_hora:.4f} Bs/h")
    col3.metric("Costo por día",      f"{C_dit_dia:.2f} Bs/día")

    st.markdown(f"""
<div class="formula-box">
C_DIT = W_COMP × Tarifa_ELEC × Horas
      = {W_COMP:.3f} kW × {TARIFA_E:.2f} Bs/kWh × {HORAS:.1f} h
      = {C_dit_dia:.2f} Bs/día
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Sistema Tritérmico — gas natural + bomba</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Q_GEN",         f"{Q_GEN_calc:.2f} kW")
    col2.metric("V_GN consumido",f"{V_GN:.4f} m³/h")
    col3.metric("Costo GN/hora", f"{C_GN_hora:.4f} Bs/h")
    col4.metric("Costo total/día",f"{C_tri_dia:.2f} Bs/día")

    st.markdown(f"""
<div class="formula-box">
V_GN  = Q_GEN / (PC_GN × η_q)
      = {Q_GEN_calc:.3f} / ({PC_GN} × {ETA_Q})
      = {V_GN:.5f} m³/h

C_GN    = {V_GN:.5f} × {TARIFA_G:.2f} = {C_GN_hora:.5f} Bs/h
C_BOMBA = {W_BOMBA:.5f} × {TARIFA_E:.2f} = {C_bomba_hora:.6f} Bs/h

C_TRI = ({C_GN_hora:.5f} + {C_bomba_hora:.6f}) × {HORAS:.1f}
      = {C_tri_dia:.2f} Bs/día
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Tabla comparativa final</div>', unsafe_allow_html=True)
    df_comp = pd.DataFrame({
        "Sistema":     ["Ditérmico (R404A)", "Tritérmico (NH₃-H₂O)"],
        "Elemento":    ["Compresor eléctrico", "Bomba + Gas Natural"],
        "Potencia":    [f"{W_COMP:.2f} kW", f"{W_BOMBA*1000:.2f} W"],
        "COP":         [f"{COP_dit_base:.3f}", f"{COP_tri:.4f}"],
        "Costo/día":   [f"{C_dit_dia:.1f} Bs", f"{C_tri_dia:.1f} Bs"],
        "Ahorro":      ["—", f"{ahorro_dia:.1f} Bs/día ({ahorro_pct:.1f}%)"]
    })
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    if ahorro_dia > 0:
        st.success(f"✅ Ahorro diario con sistema tritérmico: **{ahorro_dia:.2f} Bs/día** ({ahorro_pct:.1f}%)")
        meses = ahorro_dia * 30
        anios = ahorro_dia * 365
        col1, col2 = st.columns(2)
        col1.metric("Ahorro mensual", f"{meses:.1f} Bs")
        col2.metric("Ahorro anual",   f"{anios:.1f} Bs")
    else:
        st.warning(f"⚠️ Con estos parámetros el ditérmico es más barato en {-ahorro_dia:.2f} Bs/día")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 6 — GRÁFICAS
# ═════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("### 📈 Gráficas comparativas")

    # ── Gráfica 1: Comparación COP ──
    fig_cop = go.Figure()
    fig_cop.add_bar(
        x=["COP Carnot\n(ideal)", "Ditérmico\n(R404A)", "Tritérmico\n(NH₃-H₂O)"],
        y=[COP_CARNOT, COP_dit_base, COP_tri],
        marker_color=["#378ADD", "#1D9E75", "#D85A30"],
        text=[f"{COP_CARNOT:.3f}", f"{COP_dit_base:.3f}", f"{COP_tri:.4f}"],
        textposition="outside"
    )
    fig_cop.update_layout(
        title="Comparación de COP — Carnot vs Ditérmico vs Tritérmico",
        yaxis_title="COP [-]", paper_bgcolor="#0f3460", plot_bgcolor="#16213e",
        font_color="white", title_font_color="#85B7EB", height=380
    )
    st.plotly_chart(fig_cop, use_container_width=True)

    col_g1, col_g2 = st.columns(2)

    # ── Gráfica 2: Costos ──
    with col_g1:
        fig_cost = go.Figure()
        fig_cost.add_bar(
            x=["Ditérmico", "Tritérmico"],
            y=[C_dit_dia, C_tri_dia],
            marker_color=["#E24B4A", "#1D9E75"],
            text=[f"{C_dit_dia:.1f} Bs", f"{C_tri_dia:.1f} Bs"],
            textposition="outside"
        )
        fig_cost.update_layout(
            title=f"Costo diario ({HORAS:.0f} h/día)",
            yaxis_title="Bs/día", paper_bgcolor="#0f3460",
            plot_bgcolor="#16213e", font_color="white",
            title_font_color="#85B7EB", height=320
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # ── Gráfica 3: Potencias ──
    with col_g2:
        fig_pow = go.Figure()
        fig_pow.add_bar(
            x=["Ditérmico\n(Compresor)", "Tritérmico\n(Bomba)", "Tritérmico\n(Generador)"],
            y=[W_COMP, W_BOMBA, Q_GEN_calc],
            marker_color=["#E24B4A", "#1D9E75", "#EF9F27"],
            text=[f"{W_COMP:.2f} kW", f"{W_BOMBA*1000:.1f} W", f"{Q_GEN_calc:.1f} kW"],
            textposition="outside"
        )
        fig_pow.update_layout(
            title="Potencias de cada sistema",
            yaxis_title="kW", paper_bgcolor="#0f3460",
            plot_bgcolor="#16213e", font_color="white",
            title_font_color="#85B7EB", height=320
        )
        st.plotly_chart(fig_pow, use_container_width=True)

    # ── Gráfica 4: COP vs T_GEN ──
    st.markdown('<div class="section-title">Sensibilidad: COP tritérmico vs temperatura del generador</div>', unsafe_allow_html=True)
    T_gens = list(range(80, 161, 5))
    cops_tri = []
    for tg in T_gens:
        tg_k = tg + 273.15
        c = COP_CARNOT * (tg_k - T_H_K) / tg_k * FACTOR_IRR if tg_k > T_H_K else 0
        cops_tri.append(round(c, 4))

    fig_sens = go.Figure()
    fig_sens.add_scatter(x=T_gens, y=cops_tri, mode="lines+markers",
                         line=dict(color="#EF9F27", width=2),
                         marker=dict(size=6),
                         name="COP tritérmico")
    fig_sens.add_vline(x=T_GEN, line_dash="dash", line_color="#85B7EB",
                       annotation_text=f"T_GEN actual = {T_GEN}°C",
                       annotation_font_color="#85B7EB")
    fig_sens.update_layout(
        title="COP tritérmico en función de T_GEN",
        xaxis_title="T_GEN [°C]", yaxis_title="COP [-]",
        paper_bgcolor="#0f3460", plot_bgcolor="#16213e",
        font_color="white", title_font_color="#85B7EB", height=350
    )
    st.plotly_chart(fig_sens, use_container_width=True)

    # ── Gráfica 5: Costo vs Q_R ──
    st.markdown('<div class="section-title">Sensibilidad: costo diario vs capacidad frigorífica</div>', unsafe_allow_html=True)
    q_vals = [q/2 for q in range(10, 101)]
    c_dits, c_tris = [], []
    for q in q_vals:
        wc = q / COP_dit_base
        c_dits.append(round(wc * TARIFA_E * HORAS, 2))
        copt = COP_tri if COP_tri > 0 else 0.001
        qg = q / copt
        vg = qg / (PC_GN * ETA_Q)
        wb = 0.01872 * (q / 15.0)
        c_tris.append(round((vg * TARIFA_G + wb * TARIFA_E) * HORAS, 2))

    fig_qr = go.Figure()
    fig_qr.add_scatter(x=q_vals, y=c_dits, name="Ditérmico",
                       line=dict(color="#E24B4A", width=2))
    fig_qr.add_scatter(x=q_vals, y=c_tris, name="Tritérmico",
                       line=dict(color="#1D9E75", width=2))
    fig_qr.add_vline(x=Q_R, line_dash="dash", line_color="#85B7EB",
                     annotation_text=f"Q_R = {Q_R} kW",
                     annotation_font_color="#85B7EB")
    fig_qr.update_layout(
        title="Costo diario vs capacidad frigorífica",
        xaxis_title="Q_R [kW]", yaxis_title="Costo [Bs/día]",
        paper_bgcolor="#0f3460", plot_bgcolor="#16213e",
        font_color="white", title_font_color="#85B7EB",
        legend=dict(bgcolor="#0f3460"), height=350
    )
    st.plotly_chart(fig_qr, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PIE DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#B5D4F4; font-size:0.8rem;">
  🧊 Simulador Ciclos Térmicos · Universidad Técnica de Oruro · MEC 3338-A · Grupo G3<br>
  Producto: Porcino | Lugar: Robore | Refrigerante: R404A | Ciclo: Flooded Evaporator
</p>
""", unsafe_allow_html=True)
