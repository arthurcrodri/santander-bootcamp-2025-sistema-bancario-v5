# Sistema Bancário V4.2
# Desenvolvido para o Santander Bootcamp 2025
# Autor: Arthur Rodrigues

# Imports, Constantes e Classes de Transação
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

AGENCIA_PADRAO = "0001"
MAX_SAQUE = 500.00
LIMITE_SAQUES = 3
LIMITE_TRANSACOES_DIARIAS = 10

# --- NOVO DECORADOR DE LOG ---
def log_transacao(func):
    """
    Decorador que registra informações da função executada em um arquivo de log.
    """
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Formata a mensagem de log com todos os detalhes solicitados
        log_msg = (
            f"[{data_hora}] Função: '{func.__name__}' | "
            f"Argumentos: {args}, {kwargs} | "
            f"Retorno: {resultado}\n"
        )
        
        # Adiciona a mensagem ao arquivo log.txt
        try:
            with open("log.txt", "a", encoding="utf-8") as arquivo_log:
                arquivo_log.write(log_msg)
        except IOError as e:
            print(f"@@@ Erro ao escrever no arquivo de log: {e} @@@")
            
        return resultado
    return wrapper

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
    
    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        return sucesso_transacao

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        return sucesso_transacao

# Classes de Conta
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = AGENCIA_PADRAO
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)
    
    def sacar(self, valor):
        saldo = self.saldo

        if valor > saldo:
            print("\n@@@ Não é possível sacar, saldo insuficiente! @@@")
        elif valor <= 0:
            print("\n@@@ Não é possível sacar, valor inválido! @@@")
        else:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Não é possível depositar, valor inválido! @@@")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=MAX_SAQUE, limite_saques=LIMITE_SAQUES):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        if valor > self.limite:
            print("\n@@@ Não é possível sacar, valor acima do máximo permitido! @@@")
        elif numero_saques >= self.limite_saques:
            print("\n@@@ Não é possível sacar, limite de saques diários atingido! @@@")
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            Conta:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

# Classes de Cliente
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacoes_do_dia = [
            t for t in conta.historico.transacoes 
            if datetime.strptime(t['data'], "%d-%m-%Y %H:%M:%S").date() == datetime.now().date()
        ]
        
        if len(transacoes_do_dia) >= LIMITE_TRANSACOES_DIARIAS:
            print("\n@@@ Limite de 10 transações diárias excedido! @@@")
            return
            
        return transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class ContaIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            self._index += 1
            return f"""\
                Agência:\t{conta.agencia}
                Conta:\t\t{conta.numero}
                Titular:\t{conta.cliente.nome}
            """
        except IndexError:
            raise StopIteration

# Funções do Sistema
def menu():
    menu_text = """
\n================ SISTEMA BANCÁRIO V4.2 ================

    [c]\tCriar Cliente
    [cc]\tCriar Conta Corrente
    [lc]\tListar Contas

    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    
    [q]\tSair

Por favor, selecione uma opção: """
    return input(textwrap.dedent(menu_text))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ O cliente não possui contas cadastradas! @@@")
        return None

    if len(cliente.contas) == 1:
        return cliente.contas[0]
    
    print("\nO cliente possui mais de uma conta. Selecione a conta desejada:")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"[{i}] - Agência: {conta.agencia}, Conta: {conta.numero}")
    try:
        opcao = int(input("Digite o número da conta desejada: "))
        if 1 <= opcao <= len(cliente.contas):
            return cliente.contas[opcao - 1]
        else:
            print("\n@@@ Opção inválida! @@@")
    except (ValueError):
        print("\n@@@ Erro: Entrada inválida! Por favor, digite um número válido. @@@")
        return None

@log_transacao
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return False
    
    try:
        valor = float(input("Informe o valor do depósito: R$ "))
        conta = recuperar_conta_cliente(cliente)
        if not conta:
            return False
        
        transacao = Deposito(valor)
        return cliente.realizar_transacao(conta, transacao)

    except ValueError:
        print("\n@@@ Erro: Informe um valor numérico válido! @@@")
        return False

@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return False

    try:
        valor = float(input("Informe o valor do saque: R$ "))
        conta = recuperar_conta_cliente(cliente)
        if not conta:
            return False

        transacao = Saque(valor)
        return cliente.realizar_transacao(conta, transacao)

    except ValueError:
        print("\n@@@ Erro: Informe um valor numérico válido! @@@")
        return False

@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return False

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return False

    print("\n================ EXTRATO ================")
    
    transacoes = list(conta.historico.gerar_relatorio())
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in transacoes:
            print(f"{transacao['data']} - {transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}")

    print(f"\nSALDO ATUAL: R$ {conta.saldo:.2f}")
    print("==========================================")
    return True

def cadastrar_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe um cliente com esse CPF! @@@")
        return
    
    nome = input("Informe o nome do cliente: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, número - bairro - cidade/estado): ")

    novo_cliente = PessoaFisica(nome, cpf, data_nascimento, endereco)
    clientes.append(novo_cliente)
    print("\n=== Cliente cadastrado com sucesso! ===")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = ContaCorrente.nova_conta(numero=numero_conta, cliente=cliente)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    print("\n============== LISTA DE CONTAS ==============")
    if not contas:
        print("Nenhuma conta cadastrada.")
    else:
        for conta_info in ContaIterador(contas):
            print("------------------------------------------")
            print(textwrap.dedent(conta_info))
    print("==========================================")

# Lógica do programa
def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        match opcao:
            case "c":
                cadastrar_cliente(clientes)
            case "cc":
                numero_conta = len(contas) + 1
                criar_conta(numero_conta, clientes, contas)
            case "lc":
                listar_contas(contas)
            case "s":
                sacar(clientes)
            case "d":
                depositar(clientes)
            case "e":
                exibir_extrato(clientes)
            case "q":
                print("\nObrigado por usar nossos serviços! Volte sempre!\n")
                break
            case _:
                print("\n@@@ Opção inválida. Por favor, selecione novamente. @@@")

        input("\nPressione ENTER para continuar...")

# Execução do Programa
if __name__ == "__main__":
    main()
