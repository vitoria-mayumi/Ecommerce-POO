// Itens que estão sendo montados no pedido atual
let itensDoPedido = [];

// Catálogo carregado da API (usado para montar os selects)
let catalogo = [];


/* ======================== Comunicação ======================== */

// Faz a requisição e devolve o campo "dados" da resposta da API.
// A API sempre responde no formato { sucesso, mensagem, dados }.
async function api(metodo, rota, corpo) {
    const opcoes = { method: metodo, headers: {} };

    if (corpo) {
        opcoes.headers["Content-Type"] = "application/json";
        opcoes.body = JSON.stringify(corpo);
    }

    const resposta = await fetch(rota, opcoes);
    const json = await resposta.json();

    if (!json.sucesso) {
        alert(json.mensagem);
        throw new Error(json.mensagem);
    }

    return json.dados;
}


// Formata um número como dinheiro: 1378.9 -> "R$ 1.378,90"
function dinheiro(valor) {
    return Number(valor).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}


/* ========================= Produtos ========================== */

// Mostra apenas os campos que fazem sentido para o tipo escolhido
function trocarTipo() {
    const tipo = document.getElementById("produto-tipo").value;

    document.getElementById("produto-estoque").className =
        tipo === "fisico" ? "" : "escondido";

    document.getElementById("produto-frete").className =
        tipo === "fisico" ? "" : "escondido";

    document.getElementById("produto-prazo").className =
        tipo === "servico" ? "" : "escondido";
}


async function salvarProduto() {
    const tipo = document.getElementById("produto-tipo").value;

    const produto = {
        codigo: document.getElementById("produto-codigo").value,
        nome: document.getElementById("produto-nome").value,
        tipo: tipo,
        preco: document.getElementById("produto-preco").value
    };

    // Cada tipo de produto tem seus campos próprios
    if (tipo === "fisico") {
        produto.estoque = document.getElementById("produto-estoque").value;
        produto.frete = document.getElementById("produto-frete").value || 0;
    }

    if (tipo === "servico") {
        produto.prazo_execucao = document.getElementById("produto-prazo").value;
    }

    await api("POST", "/produtos", produto);
    alert("Produto cadastrado!");

    document.getElementById("produto-codigo").value = "";
    document.getElementById("produto-nome").value = "";
    document.getElementById("produto-preco").value = "";
    document.getElementById("produto-estoque").value = "";
    document.getElementById("produto-frete").value = "";
    document.getElementById("produto-prazo").value = "";

    carregarProdutos();
}


// Desenha a tabela do catálogo
function mostrarProdutos(produtos, avisoVazio) {
    let html = "";

    for (const p of produtos) {
        // Detalhes mudam conforme o tipo (polimorfismo na prática)
        let detalhes = "Entrega eletrônica";

        if (p.tipo === "fisico") {
            detalhes = "Frete: " + dinheiro(p.frete);
        } else if (p.tipo === "servico") {
            detalhes = "Prazo: " + p.prazo_execucao_dias + " dias";
        }

        // Só produto físico tem estoque para ajustar
        const ajuste = p.tipo === "fisico"
            ? `<input type="number" id="ajuste-${p.id}" value="1" size="3">
               <button onclick="ajustarEstoque(${p.id}, 1)">+</button>
               <button onclick="ajustarEstoque(${p.id}, -1)">-</button>`
            : "-";

        html += `<tr>
            <td>${p.codigo}</td>
            <td>${p.nome}</td>
            <td><span class="tipo tipo-${p.tipo}">${p.tipo}</span></td>
            <td>${dinheiro(p.preco)}</td>
            <td>${p.tipo === "fisico" ? p.estoque : "-"}</td>
            <td>${detalhes}</td>
            <td>${ajuste}</td>
        </tr>`;
    }

    if (produtos.length === 0) {
        html = `<tr class="vazio"><td colspan="7">${avisoVazio}</td></tr>`;
    }

    document.getElementById("tabela-produtos").innerHTML = html;
}


async function carregarProdutos() {
    catalogo = await api("GET", "/produtos");
    mostrarProdutos(catalogo, "Nenhum produto cadastrado ainda");
    preencherSelectProdutos();
}


async function buscarProdutos() {
    const nome = document.getElementById("produto-busca").value;
    const produtos = await api("GET", "/produtos/busca?nome=" + nome);
    mostrarProdutos(produtos, "Nenhum produto encontrado nessa busca");
}


// A API trata a quantidade como ajuste: positivo entra, negativo sai
async function ajustarEstoque(produtoId, sinal) {
    const quantidade = document.getElementById("ajuste-" + produtoId).value;

    await api("PATCH", "/produtos/" + produtoId + "/estoque", {
        quantidade: Number(quantidade) * sinal
    });

    carregarProdutos();
}


/* ========================= Clientes ========================== */

async function salvarCliente() {
    const cliente = {
        nome: document.getElementById("cliente-nome").value,
        email: document.getElementById("cliente-email").value,
        endereco: document.getElementById("cliente-endereco").value
    };

    await api("POST", "/clientes", cliente);
    alert("Cliente cadastrado!");

    document.getElementById("cliente-nome").value = "";
    document.getElementById("cliente-email").value = "";
    document.getElementById("cliente-endereco").value = "";

    carregarClientes();
}


async function carregarClientes() {
    const clientes = await api("GET", "/clientes");

    let html = "";

    for (const c of clientes) {
        html += `<tr>
            <td>${c.id}</td>
            <td>${c.nome}</td>
            <td>${c.email}</td>
            <td>${c.endereco}</td>
        </tr>`;
    }

    if (clientes.length === 0) {
        html = `<tr class="vazio">
            <td colspan="4">Nenhum cliente cadastrado ainda</td>
        </tr>`;
    }

    document.getElementById("tabela-clientes").innerHTML = html;

    // Os dois selects de cliente usam a mesma lista
    let opcoes = "";

    for (const c of clientes) {
        opcoes += `<option value="${c.id}">${c.nome}</option>`;
    }

    document.getElementById("pedido-cliente").innerHTML = opcoes;
    document.getElementById("pedido-historico").innerHTML = opcoes;
}


/* ========================== Pedidos ========================== */

function preencherSelectProdutos() {
    let opcoes = "";

    for (const p of catalogo) {
        opcoes += `<option value="${p.id}">${p.nome} - ${dinheiro(p.preco)}</option>`;
    }

    document.getElementById("pedido-produto").innerHTML = opcoes;
}


function adicionarItem() {
    const produtoId = Number(document.getElementById("pedido-produto").value);
    const quantidade = Number(document.getElementById("pedido-quantidade").value);

    const produto = catalogo.find(p => p.id === produtoId);

    itensDoPedido.push({
        produto_id: produtoId,
        quantidade: quantidade,
        nome: produto.nome
    });

    mostrarItens();
}


function mostrarItens() {
    let html = "";

    // O indice e usado para saber qual item remover da lista
    for (let i = 0; i < itensDoPedido.length; i++) {
        const item = itensDoPedido[i];

        html += `<tr>
            <td>${item.nome}</td>
            <td>${item.quantidade}</td>
            <td><button class="excluir" onclick="removerItem(${i})">Excluir</button></td>
        </tr>`;
    }

    // Sem isso a tabela fica so com o cabecalho solto na tela
    if (itensDoPedido.length === 0) {
        html = `<tr class="vazio">
            <td colspan="3">Nenhum item adicionado ainda</td>
        </tr>`;
    }

    document.getElementById("tabela-itens").innerHTML = html;
}


// Tira um item do pedido que ainda esta sendo montado
function removerItem(indice) {
    itensDoPedido.splice(indice, 1);
    mostrarItens();
}


async function criarPedido() {
    const pedido = {
        cliente_id: Number(document.getElementById("pedido-cliente").value),
        itens: itensDoPedido.map(item => ({
            produto_id: item.produto_id,
            quantidade: item.quantidade
        }))
    };

    const criado = await api("POST", "/pedidos", pedido);
    alert("Pedido criado! Total: " + dinheiro(criado.total));

    itensDoPedido = [];
    mostrarItens();

    // O pedido dá baixa no estoque, então recarregamos o catálogo
    carregarProdutos();
}


async function verPedidos() {
    const clienteId = document.getElementById("pedido-historico").value;
    const pedidos = await api("GET", "/clientes/" + clienteId + "/pedidos");

    let html = "";

    for (const pedido of pedidos) {
        let linhas = "";

        for (const item of pedido.itens) {
            linhas += `<tr>
                <td>${item.produto}</td>
                <td>${item.quantidade}</td>
                <td>${dinheiro(item.preco_unitario)}</td>
                <td>${dinheiro(item.total_item)}</td>
            </tr>`;
        }

        // A data vem em UTC sem fuso, por isso o "Z" no final
        const data = new Date(pedido.data_criacao + "Z").toLocaleString("pt-BR");

        html += `<div class="pedido">
            <h4>Pedido #${pedido.id} - ${data} - Total: ${dinheiro(pedido.total)}</h4>
            <table>
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Qtd</th>
                        <th>Preço</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>${linhas}</tbody>
            </table>
        </div>`;
    }

    if (pedidos.length === 0) {
        html = "<p>Este cliente ainda não tem pedidos.</p>";
    }

    document.getElementById("lista-pedidos").innerHTML = html;
}


/* ========================= Relatório ========================= */

async function carregarRelatorio() {
    const dados = await api("GET", "/relatorios/vendas");

    document.getElementById("relatorio-totais").innerHTML = `
        Faturamento de produtos: <b>${dinheiro(dados.faturamento_produtos || 0)}</b><br>
        Faturamento de frete: <b>${dinheiro(dados.faturamento_frete || 0)}</b><br>
        Faturamento total: <b>${dinheiro(dados.faturamento_total)}</b>`;

    let html = "";

    for (const item of dados.produtos_mais_vendidos) {
        html += `<tr>
            <td>${item.codigo}</td>
            <td>${item.nome}</td>
            <td>${item.quantidade_vendida}</td>
            <td>${dinheiro(item.faturamento)}</td>
        </tr>`;
    }

    if (dados.produtos_mais_vendidos.length === 0) {
        html = `<tr class="vazio">
            <td colspan="4">Nenhum produto cadastrado para gerar o ranking</td>
        </tr>`;
    }

    document.getElementById("tabela-relatorio").innerHTML = html;
}


/* ========================= Navegação ========================= */

// Mostra uma tela e esconde as outras
function mostrarTela(nome) {
    for (const tela of document.querySelectorAll(".tela")) {
        tela.className = "tela escondido";
    }

    document.getElementById("tela-" + nome).className = "tela";

    // Destaca o botao do menu da tela atual
    for (const botao of document.querySelectorAll("#menu button")) {
        botao.className = botao.dataset.tela === nome ? "ativo" : "";
    }

    // O relatorio e gerado na hora de abrir, para nao ficar vazio
    if (nome === "relatorio") {
        carregarRelatorio();
    }
}


/* ======================== Inicialização ====================== */

mostrarTela("produtos");
trocarTipo();
mostrarItens();
carregarProdutos();
carregarClientes();
