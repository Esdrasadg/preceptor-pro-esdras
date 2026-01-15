import streamlit as st

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Preceptor Pro v31", page_icon="👨‍⚕️", layout="wide")

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

# --- 3. DADOS MÉDICOS ---
wfa_boys = {0: [0.3487, 3.346, 0.146], 3: [0.1395, 6.421, 0.118], 6: [0.0120, 7.932, 0.109], 12: [-0.142, 9.643, 0.105], 24: [-0.298, 12.15, 0.105], 60: [-0.355, 18.29, 0.115]}
wfa_girls = {0: [0.3907, 3.232, 0.150], 3: [0.1878, 5.845, 0.117], 6: [0.0567, 7.297, 0.108], 12: [-0.088, 8.952, 0.104], 24: [-0.243, 11.48, 0.105], 60: [-0.309, 18.21, 0.118]}
len_boys = {0: [1, 49.88, 0.038], 12: [1, 75.75, 0.034]}; hgt_boys = {24: [1, 87.1, 0.036], 60: [1, 110.0, 0.039]}
len_girls = {0: [1, 49.15, 0.038], 12: [1, 74.02, 0.035]}; hgt_girls = {24: [1, 85.7, 0.037], 60: [1, 109.4, 0.040]}
hc_boys = {0: [1, 34.5, 0.036], 12: [1, 46.1, 0.029], 60: [1, 50.8, 0.028]}
hc_girls = {0: [1, 33.9, 0.036], 12: [1, 44.9, 0.029], 60: [1, 49.9, 0.028]}

def get_lms(db, age): return db[min(db.keys(), key=lambda x: abs(x-age))]
def calc_z(val, l, m, s): return ((val/m)**l-1)/(l*s) if val>0 else 0

# --- 4. MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=60)
    st.title("Preceptor Pro")
    st.caption("Criado por: **Esdras Guerra**") # NOME CORRIGIDO AQUI
    
    if ia_ativa: st.success(status_txt)
    else: st.error(status_txt)
    
    st.divider()
    menu = st.radio("Selecione:", ["💊 Mestre das Doses", "💧 Renal KDIGO", "❤️ Cardio SBC", "👶 Puericultura", "🤖 Chat"])

# --- 5. POSOLOGIA ---
if menu == "💊 Mestre das Doses":
    st.header("💊 Calculadora Pediátrica")
    peso = st.number_input("Peso (kg)", 3.0, 80.0, 10.0, step=0.5)
    
    t1, t2, t3, t4 = st.tabs(["🤒 Febre/Dor", "🦠 Antibióticos", "🤧 Outros", "🧠 IA (Livre)"])
    
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
                except Exception as e:
                    st.error(f"Erro ao gerar: {e}")
            else: st.error("IA Offline")

# --- 6. RENAL KDIGO (COMPLETA) ---
elif menu == "💧 Renal KDIGO":
    st.header("💧 Função Renal (KDIGO 2012)")
    
    st.info("Calculadora de Prognóstico de Doença Renal Crônica")
    
    c1, c2 = st.columns(2)
    cr = c1.number_input("Creatinina (mg/dL)", 0.1, 15.0, 1.0, step=0.1)
    idd = c1.number_input("Idade (anos)", 18, 120, 60)
    sx = c2.selectbox("Sexo", ["Masculino", "Feminino"])
    rac = c2.number_input("Albuminúria (mg/g ou mg/24h)", 0, 5000, 10)
    
    if st.button("CALCULAR ESTRATIFICAÇÃO"):
        # 1. Cálculo TFG (CKD-EPI)
        k = 0.7 if sx == "Feminino" else 0.9
        a = -0.241 if sx == "Feminino" else -0.302
        f = 1.012 if sx == "Feminino" else 1.0
        
        tfg = 142 * ((min(cr/k, 1))**a) * ((max(cr/k, 1))**-1.200) * (0.9938**idd) * f
        
        # 2. Classificação G (TFG)
        g_stg = ""
        if tfg >= 90: g_stg = "G1 (Normal/Alto)"
        elif tfg >= 60: g_stg = "G2 (Levemente diminuído)"
        elif tfg >= 45: g_stg = "G3a (Leve a moderado)"
        elif tfg >= 30: g_stg = "G3b (Moderado a grave)"
        elif tfg >= 15: g_stg = "G4 (Grave)"
        else: g_stg = "G5 (Falência renal)"
        
        # 3. Classificação A (Albuminúria)
        a_stg = ""
        if rac < 30: a_stg = "A1 (Normal)"
        elif rac <= 300: a_stg = "A2 (Moderadamente aumentada)"
        else: a_stg = "A3 (Gravemente aumentada)"
        
        # 4. Matriz de Risco (Cores)
        risco = "Baixo Risco"; cor = "success"
        
        g_cod = int(g_stg[1]) # Pega o numero 1, 2, 3, 4, 5
        if "G3a" in g_stg: g_cod = 3.0
        elif "G3b" in g_stg: g_cod = 3.5
        
        if g_cod >= 4 or (rac > 300) or (g_cod == 3.5 and rac > 30):
            risco = "MUITO ALTO RISCO (Vermelho)"; cor = "error"
        elif (g_cod == 3.5) or (g_cod == 3.0 and rac > 30) or (g_cod <= 2 and rac > 30):
            risco = "ALTO RISCO (Laranja)"; cor = "warning"
        elif (g_cod == 3.0 and rac < 30):
            risco = "MODERADO RISCO (Amarelo)"; cor = "warning"
        
        st.divider()
        col_res1, col_res2 = st.columns(2)
        
        col_res1.metric("eGFR (TFG)", f"{tfg:.1f}", f"{g_stg.split()[0]}")
        col_res1.caption(g_stg)
        col_res2.metric("Classificação", f"{g_stg.split()[0]} + {a_stg.split()[0]}")
        col_res2.caption(a_stg)
        
        if cor == "success": st.success(risco)
        elif cor == "error": st.error(risco)
        else: st.warning(risco)

# --- 7. CARDIO SBC ---
elif menu == "❤️ Cardio SBC":
    st.header("❤️ Risco Cardiovascular")
    prev = st.radio("Evento Prévio (Infarto/AVC)?", ["Não", "Sim"], horizontal=True)
    
    if prev == "Sim":
        st.error("🚨 MUITO ALTO RISCO")
        st.metric("Meta LDL", "< 50 mg/dL")
    else:
        c1, c2 = st.columns(2)
        idade = c1.number_input("Idade", 20, 100, 50)
        ldl = c1.number_input("LDL", 20, 600, 130)
        dm = c2.checkbox("Diabetes"); drc = c2.checkbox("Doença Renal")
        fumo = c2.checkbox("Tabagismo"); has = c2.checkbox("Hipertensão > 180")
        
        if st.button("CALCULAR"):
            r="BAIXO"; m="< 130"; c="green"
            if drc or (dm and ldl>=190) or ldl>=190: r="MUITO ALTO"; m="< 50"; c="red"
            elif dm or ldl>=160 or (has and fumo): r="ALTO"; m="< 70"; c="orange"
            elif ldl>=130 or fumo or idade>65: r="INTERMEDIÁRIO"; m="< 100"; c="blue"
            st.markdown(f"### :{c}[{r}]"); st.metric("Meta LDL", m)

# --- 8. PUERICULTURA ---
elif menu == "👶 Puericultura":
    st.header("👶 Crescimento OMS")
    c1, c2 = st.columns(2)
    sexo = c1.selectbox("Sexo", ["Menino", "Menina"])
    idade = c2.number_input("Idade (meses)", 0.0, 60.0, 6.0)
    semanas = c1.number_input("IG Nascer", 24, 42, 40)
    peso = c2.number_input("Peso (kg)", 0.0, 40.0, 7.0)
    alt = c1.number_input("Est/Comp (cm)", 0.0, 150.0, 65.0)
    pc = c2.number_input("PC (cm)", 0.0, 60.0, 42.0)
    
    if semanas < 37 and idade <= 24:
        idade = max(0, idade - ((40-semanas)/4.3))
        st.warning(f"⚠️ Idade Corrigida: {idade:.1f} m")
        
    if st.button("Calcular Z-Score"):
        dbs = lambda b,g: b if sexo=="Menino" else g
        zp = calc_z(peso, *get_lms(dbs(wfa_boys, wfa_girls), idade))
        dba = dbs(len_boys, len_girls) if idade<24 else dbs(hgt_boys, hgt_girls)
        za = calc_z(alt, *get_lms(dba, idade))
        zpc = calc_z(pc, *get_lms(dbs(hc_boys, hc_girls), idade))
        c = st.columns(3)
        c[0].metric("Z-Peso", f"{zp:.2f}", delta_color="normal" if abs(zp)<=2 else "inverse")
        c[1].metric("Z-Alt", f"{za:.2f}", delta_color="normal" if abs(za)<=2 else "inverse")
        c[2].metric("Z-PC", f"{zpc:.2f}", delta_color="normal" if abs(zpc)<=2 else "inverse")

# --- 9. CHAT ---
elif menu == "🤖 Chat":
    st.header("Chat Clínico")
    if ia_ativa:
        if "chat" not in st.session_state: st.session_state["chat"] = []
        for r,t in st.session_state["chat"]:
            with st.chat_message(r): st.write(t)
        if m:=st.chat_input("Caso..."):
            st.session_state["chat"].append(("user", m))
            with st.chat_message("user"): st.write(m)
            with st.chat_message("assistant"):
                try:
                    r = model.generate_content(f"Médico. {m}").text
                    st.write(r); st.session_state["chat"].append(("assistant", r))
                except: st.error("Erro.")
    else: st.error("Offline")