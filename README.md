# Sistema Bancário V5 🏦

Projeto de simulação de um sistema bancário via linha de comando, desenvolvido como desafio para o Santander Bootcamp 2025. Esta versão (V5) foca na refatoração do código para utilizar Programação Orientada a Objetos (POO) e na implementação de funcionalidades avançadas como logging de transações e iteradores.

## 📋 Funcionalidades

O sistema permite ao usuário realizar as seguintes operações bancárias básicas:

##### Gestão de Usuários:

- `[c]` - Criar Cliente (Pessoa Física)

##### Gestão de Contas:

- `[cc]` - Criar Conta Corrente (vinculada a um cliente)

- `[lc]` - Listar todas as Contas cadastradas

##### Operações Bancárias:

- `[d]` - Realizar um Depósito

- `[s]` - Realizar um Saque

- `[e]` - Exibir Extrato

##### Outras:

- `[q]` - Sair do sistema

## 💡 Conceitos e Tecnologias Aplicadas

O principal objetivo deste projeto foi aplicar conceitos avançados de Python e Programação Orientada a Objetos.

### 1. Programação Orientada a Objetos (POO)

O código foi totalmente reestruturado em torno de classes para representar as entidades do sistema:

- `Cliente` e `PessoaFisica`: Utiliza Herança para especializar o cliente.

- `Conta` e `ContaCorrente`: A `ContaCorrente` herda de Conta e aplica Polimorfismo ao sobrescrever o método sacar com novas regras de negócio (limite de saques e valor máximo).

- `Historico`: Classe dedicada a gerenciar as transações de uma conta.

- `Transacao` (Classe Abstrata - ABC): Define a "interface" para as classes `Deposito` e `Saque`, garantindo que ambas implementem os métodos necessários.

### 2. Decorators

- `@log_transacao`: Um decorador customizado foi criado para auditar e registrar todas as operações financeiras (depósito, saque e extrato).

- Logging: Qualquer função decorada com `@log_transacao` terá seus argumentos, retorno e data/hora salvos automaticamente no arquivo log.txt.

### 3. Iteradores e Geradores

- Iterador (`ContaIterador`): Foi implementada uma classe iteradora para a função "Listar Contas". Isso permite percorrer a lista de contas de forma mais elegante e controlada.

- Gerador (`Historico.gerar_relatorio`): O método que gera o extrato utiliza yield, transformando-se em um gerador. Isso é mais eficiente em termos de memória, pois não precisa carregar todas as transações de uma vez.

### 4. Regras de Negócio

O sistema implementa as seguintes regras de negócio na classe `ContaCorrente`:

- Limite de Saques: Máximo de 3 saques diários.

- Valor Limite por Saque: Máximo de R$ 500,00 por saque.

- Limite de Transações: Máximo de 10 transações (depósitos ou saques) por dia.

## 🚀 Como Executar

Certifique-se de ter o Python 3.x instalado.

##### 1. Clone este repositório:

```bash
git clone https://github.com/arthurcrodri/santander-bootcamp-2025-sistema-bancario-v5.git
```

##### 2. Navegue até o diretório do projeto:

```bash
cd santander-bootcamp-2025-sistema-bancario-v5
```

##### 3. Execute o script principal:

```bash
python sistema_bancario_v5.py
```

- Opcional: Verifique o arquivo log.txt que será criado no mesmo diretório após realizar transações.

##👤 Autor

Arthur Rodrigues
- [LinkedIn](https://linkedin.com/in/arthurcrodri);
- [GitHub](https://github.com/arthurcrodri).
