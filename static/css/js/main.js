function registrarEntrada() {
    const placa = document.getElementById('fluxo-placa').value;
    const tipo_vaga = document.getElementById('fluxo-vaga').value;

    if (!placa) return alert('Por favor, digite a placa!');

    fetch('/api/entrada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ placa, tipo_vaga })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        document.getElementById('fluxo-placa').value = '';
    });
}

function registrarSaida() {
    const placa = document.getElementById('fluxo-placa').value;

    if (!placa) return alert('Por favor, digite a placa!');

    fetch('/api/saida', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ placa })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        document.getElementById('fluxo-placa').value = '';
    });
}

function cadastrarCliente(event) {
    event.preventDefault();

    const dados = {
        nome: document.getElementById('cad-nome').value,
        telefone: document.getElementById('cad-tel').value,
        plano: document.getElementById('cad-plano').value,
        placa: document.getElementById('cad-placa').value,
        modelo: document.getElementById('cad-modelo').value,
        cor: document.getElementById('cad-cor').value,
        tipo: document.getElementById('cad-tipo').value
    };

    fetch('/api/cadastro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        document.getElementById('form-cadastro').reset();
    });
}