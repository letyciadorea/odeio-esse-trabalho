from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            tipo_plano TEXT DEFAULT 'Rotativo' -- Rotativo, Mensalista, Anual
        )
    ''')
    
    # Tabela de Veículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            planca TEXT UNIQUE NOT NULL,
            modelo TEXT,
            cor TEXT,
            tipo TEXT, -- Normal ou Preferencial
            FOREIGN KEY(id_cliente) REFERENCES clientes(id)
        )
    ''')
    
    # Tabela de Fluxo do Estacionamento (Controle de Placas e Valores)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            tipo_vaga TEXT, -- Normal / Preferencial
            entrada TEXT NOT NULL,
            saida TEXT,
            valor_pago REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# Inicializa o banco de dados ao rodar o app
init_db()

# CONFIGURAÇÃO DE PREÇOS
PRECO_HORA = 10.00
PRECO_DIARIA = 60.00

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/relatorios_page')
def relatorios_page():
    return render_template('relatorios.html')

# API: Registrar Entrada de Veículo
@app.route('/api/entrada', methods=['POST'])
def entrada_veiculo():
    dados = request.json
    placa = dados.get('placa')
    tipo_vaga = dados.get('tipo_vaga') # 'Normal' ou 'Preferencial'
    hora_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO registros (placa, tipo_vaga, entrada) VALUES (?, ?, ?)", 
                       (placa, tipo_vaga, hora_entrada))
        conn.commit()
        return jsonify({"status": "sucesso", "mensagem": f"Entrada da placa {placa} registrada!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})
    finally:
        conn.close()

# API: Registrar Saída e Calcular Valor
@app.route('/api/saida', methods=['POST'])
def saida_veiculo():
    dados = request.json
    placa = dados.get('placa')
    hora_saida = datetime.now()
    hora_saida_str = hora_saida.strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Busca o registro aberto mais recente para essa placa
    cursor.execute("SELECT id, entrada FROM registros WHERE placa = ? AND saida IS NULL ORDER BY id DESC LIMIT 1", (placa,))
    registro = cursor.fetchone()

    if not registro:
        conn.close()
        return jsonify({"status": "erro", "mensagem": "Placa não encontrada ou já saiu."})

    reg_id, entrada_str = registro
    entrada = datetime.strptime(entrada_str, '%Y-%m-%d %H:%M:%S')
    
    # Cálculo do tempo e valor
    duracao = hora_saida - entrada
    horas = max(1, ceil(duracao.total_seconds() / 3600)) # Mínimo de 1 hora
    
    valor_total = horas * PRECO_HORA
    if valor_total > PRECO_DIARIA:
        valor_total = PRECO_DIARIA

    # Atualiza o banco com a saída e valor
    cursor.execute("UPDATE registros SET saida = ?, valor_pago = ? WHERE id = ?", (hora_saida_str, valor_total, reg_id))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "sucesso",
        "mensagem": f"Saída liberada. Tempo: {horas}h. Valor a pagar: R$ {valor_total:.2f}"
    })

# API: Cadastrar Cliente e Veículo juntos
@app.route('/api/cadastro', methods=['POST'])
def cadastrar_cliente_veiculo():
    dados = request.json
    nome = dados.get('nome')
    telefone = dados.get('telefone')
    plano = dados.get('plano')
    placa = dados.get('placa')
    modelo = dados.get('modelo')
    cor = dados.get('cor')
    tipo = dados.get('tipo')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome, telefone, tipo_plano) VALUES (?, ?, ?)", (nome, telefone, plano))
        cliente_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO veiculos (id_cliente, planca, modelo, cor, tipo) VALUES (?, ?, ?, ?, ?)", 
                       (cliente_id, placa, modelo, cor, tipo))
        conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Cliente e Veículo cadastrados!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})
    finally:
        conn.close()

# API: Relatório de Movimentação
@app.route('/api/relatorio', methods=['GET'])
def obter_relatorio():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT placa, tipo_vaga, entrada, saida, valor_pago FROM registros")
    dados = cursor.fetchall()
    conn.close()

    relatorio = []
    for linha in dados:
        relatorio.append({
            "placa": linha[0],
            "tipo_vaga": linha[1],
            "entrada": linha[2],
            "saida": linha[3] if linha[3] else "No pátio",
            "valor": f"R$ {linha[4]:.2f}" if linha[4] else "-"
        })
    return jsonify(relatorio)

# Função auxiliar para arredondar horas para cima
from math import ceil

if __name__ == '__main__':
    app.run(debug=True)