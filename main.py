# Sistema Bancário V4
# Desenvolvido para o Santander Bootcamp 2025
# Autor: Arthur Rodrigues

# Imports, Constantes e Classes de Transação
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

AGENCIA_PADRAO = "0001"
MAX_SAQUE = 500.00
LIMITE_SAQUES = 3

# --- DECORADOR DE LOG ---
def log_transacao(func):
    def wrapper(*args, **kwargs):
        data_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        resultado = func(*args, **kwargs)
        print(f"---------------------------------------------------\n{data_hora} - Operação '{func.__name__.upper()}' executada com sucesso!")
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
    
    # --- GERADOR DE RELATÓRIOS ---
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
            print("@@@ Não é possível sacar, saldo insuficiente! @@@\n")
        elif valor <= 0:
            print("@@@ Não é possível sacar, valor inválido! @@@")
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
            print("@@@ Não é possível depositar, valor inválido! @@@")
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
            print("@@@ Não é possível sacar, valor acima do máximo permitido! @@@\n")
        elif numero_saques >= self.limite_saques:
            print("@@@ Não é possível sacar, limite de saques diários atingido! @@@\n")
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
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

# --- ITERADOR PERSONALIZADO ---
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
\n================ SISTEMA BANCÁRIO V4 ================

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
        print("\n@@@ Cliente não encontrado! @@@\n")
        return
    
    try:
        valor = float(input("Informe o valor do depósito: R$ "))
        conta = recuperar_conta_cliente(cliente)
        if not conta:
            return
        
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)

    except ValueError:
        print("\n@@@ Erro: Informe um valor numérico válido! @@@\n")

@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@\n")
        return

    try:
        valor = float(input("Informe o valor do saque: R$ "))
        conta = recuperar_conta_cliente(cliente)
        if not conta:
            return

        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)

    except ValueError:
        print("\n@@@ Erro: Informe um valor numérico válido! @@@\n")

@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@\n")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    
    tipo_extrato = input("Deseja o extrato completo (c) ou filtrar por tipo (f)? ").lower()
    
    if tipo_extrato == 'f':
        tipo_transacao = input("Qual o tipo de transação (saque/deposito)? ").capitalize()
        transacoes_filtradas = list(conta.historico.gerar_relatorio(tipo_transacao=tipo_transacao))
        if not transacoes_filtradas:
            print(f"Não foram realizadas movimentações do tipo '{tipo_transacao}'.")
        else:
            for transacao in transacoes_filtradas:
                print(f"{transacao['data']} - {transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}")

    else:
        transacoes_completas = list(conta.historico.gerar_relatorio())
        if not transacoes_completas:
            print("Não foram realizadas movimentações.")
        else:
            for transacao in transacoes_completas:
                print(f"{transacao['data']} - {transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}")

    
    print(f"\nSALDO ATUAL: R$ {conta.saldo:.2f}")
    print("==========================================")


def cadastrar_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe um cliente com esse CPF! @@@\n")
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
        print("\n@@@ Cliente não encontrado! @@@\n")
        return

    conta_existente = [conta for conta in contas if conta.numero == numero_conta]
    if conta_existente:
        print("\n@@@ Já existe uma conta com esse número! @@@\n")
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
                # Criar Usuário
                cadastrar_cliente(clientes)

            case "cc":
                # Criar Conta Corrente
                numero_conta = len(contas) + 1
                criar_conta(numero_conta, clientes, contas)

            case "lc":
                # Listar Contas Correntes
                listar_contas(contas)

            case "s":
                # Saque
                sacar(clientes)

            case "d":
                # Depósito
                depositar(clientes)

            case "e":
                # Extrato
                exibir_extrato(clientes)

            case "q":
                print("\nObrigado por usar nossos serviços! Volte sempre!\n")
                break

            case _:
                print("\n@@@ Opção inválida. Por favor, selecione novamente. @@@\n")

        input("\nPressione ENTER para continuar...")

# Execução do Programa
if __name__ == "__main__":
    main()
