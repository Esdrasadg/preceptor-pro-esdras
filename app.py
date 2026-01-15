import streamlit as st

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Preceptor Pro v33", page_icon="👨‍⚕️", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; }
    div[data-testid="stMetricValue"] { font-size: 1.3rem; }
    .stAlert { border-radius: 12px; }
    .med-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXÃO IA (AUTO-ADAPTÁVEL) ---
ia_ativa = False
model = None
status_txt = "Iniciando..."
nome_modelo_usado = "Nenhum"

try:
    import google.generativeai as genai
    # IMPORTANTE: Se for subir pra nuvem, use st.secrets["GEMINI_KEY"]
    # Para testes locais, sua chave direta:
    MINHA_CHAVE = "AIzaSyCQclcnZKrXHkAwQVG2HQhaSx_uVh0EsNY"
    genai.configure(api_key=MINHA_CHAVE)
    
    try:
        lista_modelos = genai.list_models()
        modelos_validos = [m.name for m in lista_modelos if 'generateContent' in m.supported_generation_methods]
        
        if modelos_validos:
            preferidos = [m for m in modelos_validos if 'flash' in m or '1.5' in m]
            nome_modelo_usado = preferidos[0] if preferidos else modelos_validos[0]
            
            model = genai.GenerativeModel(nome_modelo_usado)
            ia_ativa = True
            status_txt = f"🟢 Conectado: {nome_modelo_usado.replace('models/', '')}"
        else:
            status_txt = "⚠️ Sua chave não tem acesso a modelos."
            
    except Exception as e:
        status_txt = f"⚠️ Erro ao listar: {str(e)[:40]}"

except Exception as e:
    status_txt = f"🔴 Erro Bibl: {str(e)[:40]}"

# --- 3. DADOS OMS COMPLETOS (L, M, S) ---
# Expandido para garantir precisão máxima na interpolação

# PESO x IDADE (Boys)
wfa_boys = {
    0: [0.3487, 3.346, 0.146], 1: [0.2672, 4.471, 0.134], 2: [0.1989, 5.582, 0.125],
    3: [0.1395, 6.421, 0.118], 4: [0.0864, 7.043, 0.114], 5: [0.0379, 7.524, 0.111],
    6: [-0.007, 7.915, 0.109], 7: [-0.049, 8.257, 0.108], 8: [-0.088, 8.577, 0.107],
    9: [-0.123, 8.897, 0.106], 10: [-0.156, 9.227, 0.106], 11: [-0.187, 9.571, 0.105],
    12: [-0.216, 9.932, 0.105], 15: [-0.296, 10.90, 0.106], 18: [-0.346, 12.00, 0.105],
    24: [-0.419, 13.80, 0.107], 36: [-0.467, 16.50, 0.110], 48: [-0.485, 18.70, 0.114], 
    60: [-0.490, 20.90, 0.117]
}
# PESO x IDADE (Girls)
wfa_girls = {
    0: [0.3907, 3.232, 0.150], 1: [0.3235, 4.187, 0.136], 2: [0.2592, 5.128, 0.126],
    3: [0.1979, 5.845, 0.119], 4: [0.1396, 6.405, 0.114], 5: [0.0841, 6.864, 0.111],
    6: [0.0312, 7.265, 0.109], 7: [-0.019, 7.636, 0.108], 8: [-0.067, 7.995, 0.107],
    9: [-0.112, 8.354, 0.106], 10: [-0.155, 8.718, 0.105], 11: [-0.196, 9.091, 0.105],
    12: [-0.235, 9.471, 0.105], 15: [-0.340, 10.80, 0.106], 18: [-0.396, 11.45, 0.106],
    24: [-0.486, 13.20, 0.109], 36: [-0.552, 16.00, 0.113], 48: [-0.569, 18.30, 0.117], 
    60: [-0.570, 20.60, 0.121]
}

# ESTATURA x IDADE (Boys)
len_boys = { # 0-24m Deitado
    0: [1, 49.88, 0.038], 1: [1, 54.72, 0.036], 2: [1, 58.42, 0.035],
    3: [1, 61.43, 0.034], 4: [1, 63.89, 0.033], 5: [1, 65.90, 0.033],
    6: [1, 67.62, 0.032], 9: [1, 71.97, 0.032], 12: [1, 75.75, 0.032],
    15: [1, 79.10, 0.032], 18: [1, 82.30, 0.032], 24: [1, 87.80, 0.032]
}
hgt_boys = { # 24-60m Em pé
    24: [1, 87.12, 0.032], 30: [1, 91.90, 0.033], 36: [1, 96.10, 0.033],
    48: [1, 103.3, 0.034], 60: [1, 110.0, 0.035]
}

# ESTATURA x IDADE (Girls)
len_girls = { # 0-24m Deitado
    0: [1, 49.15, 0.038], 1: [1, 53.70, 0.036], 2: [1, 57.07, 0.035],
    3: [1, 59.80, 0.034], 4: [1, 62.09, 0.033], 5: [1, 64.03, 0.033],
    6: [1, 65.73, 0.032], 9: [1, 70.14, 0.032], 12: [1, 74.02, 0.032],
    15: [1, 77.50, 0.032], 18: [1, 80.70, 0.032], 24: [1, 86.40, 0.032]
}
hgt_girls = { # 24-60m Em pé
    24: [1, 85.71, 0.032], 30: [1, 90.70, 0.033], 36: [1, 95.10, 0.033],
    48: [1, 102.7, 0.034], 60: [1, 109.4, 0.035]
}

# PERÍMETRO CEFÁLICO (Boys)
hc_boys = {
    0: [1, 34.46, 0.037], 1: [1, 37.28, 0.035], 2: [1, 39.11, 0.033],
    3: [1, 40.54, 0.032], 4: [1, 41.69, 0.031], 5: [1, 42.64, 0.030],
    6: [1, 43.36, 0.030], 9: [1, 44.97, 0.029], 12: [1, 46.06, 0.028],
    15: [1, 47.30, 0.028], 18: [1, 47.90, 0.028], 24: [1, 48.30, 0.028], 
    36: [1, 49.60, 0.028], 60: [1, 50.80, 0.028]
}
# PERÍMETRO CEFÁLICO (Girls)
hc_girls = {
    0: [1, 33.86, 0.037], 1: [1, 36.45, 0.035], 2: [1, 38.27, 0.033],
    3: [1, 39.54, 0.032], 4: [1, 40.62, 0.031], 5: [1, 41.51, 0.030],
    6: [1, 42.23, 0.030], 9: [1, 43.83, 0.029], 12: [1, 44.90, 0.028],
    15: [1, 46.10, 0.028], 18: [1, 46.80, 0.028], 24: [1, 47.20, 0.028], 
    36: [1, 48.50, 0.028], 60: [1, 49.90, 0.028]
}

# --- 4. ENGINE DE INTERPOLAÇÃO (O SEGREDO DA PRECISÃO) ---
def get_lms_interpolated(db, age):
    ages = sorted(db.keys())
    
    # Se idade for menor que o mínimo ou maior que o máximo da tabela
    if age <= ages[0]: return db[ages[0]]
    if age >= ages[-1]: return db[ages[-1]]
    
    # Algoritmo de Busca e Interpolação
    for i in range(len(ages)-1):
        # Acha entre quais meses a criança está (Ex: entre 2 e 3)
        if ages[i] <= age < ages[i+1]:
            x1, x2 = ages[i], ages[i+1]
            y1, y2 = db[x1], db[x2] # Pega [L, M, S] dos vizinhos
            
            # Calcula a fração exata (Ex: 2.5 meses -> fração 0.5)
            fraction = (age - x1) / (x2 - x1)
            
            # Interpolação Linear para L, M e S
            l = y1[0] + (y2[0] - y1[0]) * fraction
            m = y1[1] + (y2[1] - y1[1]) * fraction
            s = y1[2] + (y2[2] - y1[2]) * fraction
            
            return [l, m, s]
            
    return db[ages[0]] # Fallback de segurança

def calc_z(val, l, m, s):
    # Fórmula LMS Oficial da OMS
    if val <= 0: return 0
    return ((val / m) ** l - 1) / (l * s)

# --- 5. MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=60)
    st.title("Preceptor Pro")
    st.caption("Criado por: **Esdras Guerra**")
    
    if ia_ativa: st.success(status_txt)
    else: st.error(status_txt)
    
    st.divider()
    menu = st.radio("Selecione:", ["💊 Mestre das Doses", "💧 Renal KDIGO", "❤️ Cardio SBC", "👶 Puericultura (Alta Precisão)", "🤖 Chat"])

# --- 6. POSOLOGIA ---
if menu == "💊 Mestre das Doses":
    st.header("💊 Calculadora Pediátrica")
    peso = st.number_input("Peso (kg)", 3.0, 80.0, 10.0, step=0.5)
    
    t1, t2, t3, t4 = st.tabs(["🤒 Febre/Dor", "🦠 Antibióticos", "🤧 Outros", "🧠 IA"])
    
    with t1:
        c1, c2 = st.columns(2)
        c1.info(f"**Dipirona (500mg/mL):**\n# {int(peso)} gotas (6/6h)")
        c2.info(f"**Paracetamol (200mg/mL):**\n# {int(peso)} gotas (6/6h)")
        st.warning(f"**Ibuprofeno (100mg/mL):** {peso/2:.1f} mL (8/8h)")
    
    with t2:
        c1, c2 = st.columns(2)
        amox = (50*peso*5)/250/3
        c1.success(f"**Amoxicilina (250mg/5mL):**\n# {amox:.1f} mL (8/8h)")
        azi = (10*peso*5)/200
        c2.success(f"**Azitromicina (200mg/5mL):**\n# {azi:.1f} mL (1x/dia)")
        cefa = (50*peso*5)/250/4
        st.success(f"**Cefalexina (250mg/5mL):** {cefa:.1f} mL (6/6h)")
    
    with t3:
        onda = (0.15*peso*5)/4
        st.write(f"**Ondansetrona (4mg/5mL):** {onda:.1f} mL")
        pred = (1*peso)/3
        st.error(f"**Prednisolona (3mg/mL):** {pred:.1f} mL (1x/dia)")
        st.write(f"**Dexclorfeniramina:** {peso*0.125:.1f} mL (8/8h)")
    
    with t4:
        med = st.text_input("Nome do Remédio:")
        if st.button("Calcular via IA"):
            if ia_ativa:
                try:
                    with st.spinner(f"Usando {nome_modelo_usado}..."):
                        resp = model.generate_content(f"Pediatria. Peso {peso}kg. Medicamento {med}. Dose, volume e apresentação.")
                        st.info(resp.text)
                except Exception as e: st.error(f"Erro: {e}")
            else: st.error("Offline")

# --- 7. RENAL KDIGO ---
elif menu == "💧 Renal KDIGO":
    st.header("💧 Função Renal (KDIGO 2012)")
    c1, c2 = st.columns(2)
    cr = c1.number_input("Creatinina (mg/dL)", 0.1, 15.0, 1.0, step=0.1)
    idd = c1.number_input("Idade (anos)", 18, 120, 60)
    sx = c2.selectbox("Sexo", ["Masculino", "Feminino"])
    rac = c2.number_input("Albuminúria (mg/g)", 0, 5000, 10)
    
    if st.button("CALCULAR"):
        k = 0.7 if sx == "Feminino" else 0.9
        a = -0.241 if sx == "Feminino" else -0.302
        f = 1.012 if sx == "Feminino" else 1.0
        tfg = 142 * ((min(cr/k, 1))**a) * ((max(cr/k, 1))**-1.200) * (0.9938**idd) * f
        
        g_stg = "G1" if tfg>=90 else "G2" if tfg>=60 else "G3a" if tfg>=45 else "G3b" if tfg>=30 else "G4" if tfg>=15 else "G5"
        a_stg = "A1" if rac<30 else "A2" if rac<=300 else "A3"
        
        risco="Baixo"; cor="success"
        g_cod=int(g_stg[1]); 
        if "G3a" in g_stg: g_cod=3.0
        elif "G3b" in g_stg: g_cod=3.5
        
        if g_cod>=4 or rac>300 or (g_cod==3.5 and rac>30): risco="MUITO ALTO"; cor="error"
        elif g_cod==3.5 or (g_cod==3.0 and rac>30) or (g_cod<=2 and rac>30): risco="ALTO"; cor="warning"
        elif g_cod==3.0 and rac<30: risco="MODERADO"; cor="warning"
        
        c1.metric("eGFR", f"{tfg:.1f}", g_stg)
        c2.metric("Classificação", f"{g_stg} + {a_stg}")
        if cor=="success": st.success(risco)
        elif cor=="error": st.error(risco)
        else: st.warning(risco)

# --- 8. CARDIO SBC ---
elif menu == "❤️ Cardio SBC":
    st.header("❤️ Risco Cardiovascular")
    prev = st.radio("Evento Prévio?", ["Não", "Sim"], horizontal=True)
    if prev == "Sim":
        st.error("🚨 MUITO ALTO RISCO"); st.metric("Meta LDL", "< 50 mg/dL")
    else:
        c1, c2 = st.columns(2)
        id_ = c1.number_input("Idade", 20, 100, 50)
        ldl = c1.number_input("LDL", 20, 600, 130)
        dm = c2.checkbox("Diabetes"); drc = c2.checkbox("Renal")
        fumo = c2.checkbox("Fumo"); has = c2.checkbox("HAS > 180")
        if st.button("CALCULAR"):
            r="BAIXO"; m="< 130"; c="green"
            if drc or (dm and ldl>=190) or ldl>=190: r="MUITO ALTO"; m="< 50"; c="red"
            elif dm or ldl>=160 or (has and fumo): r="ALTO"; m="< 70"; c="orange"
            elif ldl>=130 or fumo or id_>65: r="INTERMEDIÁRIO"; m="< 100"; c="blue"
            st.markdown(f"### :{c}[{r}]"); st.metric("Meta LDL", m)

# --- 9. PUERICULTURA (COM INTERPOLAÇÃO) ---
elif menu == "👶 Puericultura (Alta Precisão)":
    st.header("👶 Crescimento OMS (Alta Precisão)")
    c1, c2 = st.columns(2)
    sexo = c1.selectbox("Sexo", ["Menino", "Menina"])
    idade = c2.number_input("Idade (meses)", 0.0, 60.0, 6.0, step=0.1, help="Aceita decimais (ex: 2.5 meses)")
    semanas = c1.number_input("IG Nascer", 24, 42, 40)
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    peso = m1.number_input("Peso (kg)", 0.0, 40.0, 7.0, step=0.05)
    lbl = "Comprimento" if idade < 24 else "Estatura"
    alt = m2.number_input(f"{lbl} (cm)", 0.0, 150.0, 65.0, step=0.5)
    pc = m3.number_input("PC (cm)", 0.0, 60.0, 42.0, step=0.5)
    
    # Cálculo Idade Corrigida
    if semanas < 37 and idade <= 24:
        idade_corr = max(0, idade - ((40-semanas)/4.3))
        st.warning(f"⚠️ Idade Corrigida: {idade_corr:.2f} meses")
        idade_calc = idade_corr
    else:
        idade_calc = idade
        
    if st.button("Calcular Z-Score (Interpolado)"):
        # Seleciona DB
        dbs = lambda b, g: b if sexo == "Menino" else g
        
        # Z-Peso
        lms_w = get_lms_interpolated(dbs(wfa_boys, wfa_girls), idade_calc)
        zp = calc_z(peso, *lms_w)
        
        # Z-Estatura
        db_alt = dbs(len_boys, len_girls) if idade_calc < 24 else dbs(hgt_boys, hgt_girls)
        lms_a = get_lms_interpolated(db_alt, idade_calc)
        za = calc_z(alt, *lms_a)
        
        # Z-PC
        lms_pc = get_lms_interpolated(dbs(hc_boys, hc_girls), idade_calc)
        zpc = calc_z(pc, *lms_pc)
        
        # Exibição
        c = st.columns(3)
        def show(col, t, v):
            col.metric(t, f"{v:.2f}", delta_color="normal" if abs(v)<=2 else "inverse", delta="Normal" if abs(v)<=2 else "Alterado")
            
        show(c[0], "Z-Peso", zp)
        show(c[1], f"Z-{lbl}", za)
        show(c[2], "Z-PC", zpc)
        st.caption("*Cálculo via Interpolação Linear (Alta Precisão OMS)")

# --- 10. CHAT ---
elif menu == "🤖 Chat":
    st.header("Chat Clínico")
    if ia_ativa:
        if "chat" not in st.session_state: st.session_state["chat"] = []
        for r,t in st.session_state["chat"]:
            with st.chat_message(r): st.write(t)
        if m:=st.chat_input("Dúvida..."):
            st.session_state["chat"].append(("user", m))
            with st.chat_message("user"): st.write(m)
            with st.chat_message("assistant"):
                try:
                    r = model.generate_content(f"Médico. {m}").text
                    st.write(r); st.session_state["chat"].append(("assistant", r))
                except: st.error("Erro.")
    else: st.error("Offline")
