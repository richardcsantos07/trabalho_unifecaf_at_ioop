"""RentSmart: orçamento de locação da R.M. Imóveis.

Aplicação de linha de comando sem dependências externas.
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


CENTAVO = Decimal("0.01")
TAXA_CONTRATUAL = Decimal("2000.00")


def dinheiro(valor: Decimal) -> Decimal:
    """Arredonda um valor monetário para centavos."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def formatar_reais(valor: Decimal) -> str:
    """Formata valores no padrão brasileiro, por exemplo R$ 1.234,56."""
    formatado = f"{dinheiro(valor):,.2f}"
    formatado = formatado.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatado}"


class Imovel(ABC):
    """Representa um tipo de imóvel e seus adicionais de aluguel."""

    descricao: str
    aluguel_base: Decimal

    @abstractmethod
    def adicionais(self) -> list[tuple[str, Decimal]]:
        """Retorna os adicionais aplicáveis antes do desconto."""

    @property
    def elegivel_desconto_sem_criancas(self) -> bool:
        return False


@dataclass(frozen=True)
class Apartamento(Imovel):
    quartos: int
    possui_criancas: bool
    vaga_garagem: bool
    descricao = "Apartamento"
    aluguel_base = Decimal("700.00")

    def __post_init__(self) -> None:
        if self.quartos not in (1, 2):
            raise ValueError("Apartamento deve ter 1 ou 2 quartos.")

    def adicionais(self) -> list[tuple[str, Decimal]]:
        itens: list[tuple[str, Decimal]] = []
        if self.quartos == 2:
            itens.append(("Adicional por 2 quartos", Decimal("200.00")))
        if self.vaga_garagem:
            itens.append(("Vaga de garagem", Decimal("300.00")))
        return itens

    @property
    def elegivel_desconto_sem_criancas(self) -> bool:
        return not self.possui_criancas


@dataclass(frozen=True)
class Casa(Imovel):
    quartos: int
    vaga_garagem: bool
    descricao = "Casa"
    aluguel_base = Decimal("900.00")

    def __post_init__(self) -> None:
        if self.quartos not in (1, 2):
            raise ValueError("Casa deve ter 1 ou 2 quartos.")

    def adicionais(self) -> list[tuple[str, Decimal]]:
        itens: list[tuple[str, Decimal]] = []
        if self.quartos == 2:
            itens.append(("Adicional por 2 quartos", Decimal("250.00")))
        if self.vaga_garagem:
            itens.append(("Vaga de garagem", Decimal("300.00")))
        return itens


@dataclass(frozen=True)
class Estudio(Imovel):
    vagas: int
    descricao = "Estúdio"
    aluguel_base = Decimal("1200.00")

    def __post_init__(self) -> None:
        if self.vagas < 2:
            raise ValueError("O pacote inicial do estúdio inclui pelo menos 2 vagas.")

    def adicionais(self) -> list[tuple[str, Decimal]]:
        valor = Decimal("250.00") + Decimal("60.00") * (self.vagas - 2)
        return [(f"Pacote de estacionamento ({self.vagas} vagas)", valor)]


@dataclass(frozen=True)
class Orcamento:
    imovel: Imovel
    quantidade_parcelas: int
    taxa_contratual: Decimal = TAXA_CONTRATUAL

    def __post_init__(self) -> None:
        if not 1 <= self.quantidade_parcelas <= 5:
            raise ValueError("A taxa contratual pode ser parcelada de 1 a 5 vezes.")

    @property
    def subtotal_aluguel(self) -> Decimal:
        return dinheiro(self.imovel.aluguel_base + sum((valor for _, valor in self.imovel.adicionais()), Decimal("0")))

    @property
    def desconto(self) -> Decimal:
        if self.imovel.elegivel_desconto_sem_criancas:
            return dinheiro(self.subtotal_aluguel * Decimal("0.05"))
        return Decimal("0.00")

    @property
    def aluguel_mensal(self) -> Decimal:
        return dinheiro(self.subtotal_aluguel - self.desconto)

    @property
    def parcelas_taxa(self) -> list[Decimal]:
        parcela_regular = dinheiro(self.taxa_contratual / self.quantidade_parcelas)
        parcelas = [parcela_regular] * (self.quantidade_parcelas - 1)
        parcelas.append(dinheiro(self.taxa_contratual - sum(parcelas, Decimal("0.00"))))
        return parcelas

    def parcela_contratual_no_mes(self, mes: int) -> Decimal:
        if 1 <= mes <= self.quantidade_parcelas:
            return self.parcelas_taxa[mes - 1]
        return Decimal("0.00")

    def exibir_resumo(self) -> None:
        print("\n" + "=" * 54)
        print("RESUMO DO ORÇAMENTO — RENTSMART")
        print("=" * 54)
        print(f"Imóvel: {self.imovel.descricao}")
        print(f"Aluguel-base: {formatar_reais(self.imovel.aluguel_base)}")
        for nome, valor in self.imovel.adicionais():
            print(f"{nome}: + {formatar_reais(valor)}")
        print(f"Subtotal antes do desconto: {formatar_reais(self.subtotal_aluguel)}")
        if self.desconto:
            print(f"Desconto de 5% (sem crianças): - {formatar_reais(self.desconto)}")
        print(f"Aluguel mensal: {formatar_reais(self.aluguel_mensal)}")
        print(f"Taxa contratual (separada do aluguel): {formatar_reais(self.taxa_contratual)}")
        print(f"Parcelamento: {self.quantidade_parcelas}x")
        for numero, parcela in enumerate(self.parcelas_taxa, start=1):
            print(f"  Parcela {numero}: {formatar_reais(parcela)}")
        print(f"Total no primeiro mês: {formatar_reais(self.aluguel_mensal + self.parcela_contratual_no_mes(1))}")
        print("=" * 54)

    def gerar_projecao_csv(self, caminho: Path) -> None:
        """Gera 12 meses, discriminando aluguel e taxa contratual."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow(["Mês", "Aluguel mensal (R$)", "Parcela da taxa (R$)", "Total previsto (R$)", "Saldo da taxa (R$)"])
            saldo = self.taxa_contratual
            for mes in range(1, 13):
                parcela = self.parcela_contratual_no_mes(mes)
                saldo = dinheiro(saldo - parcela)
                writer.writerow([
                    mes,
                    self._decimal_csv(self.aluguel_mensal),
                    self._decimal_csv(parcela),
                    self._decimal_csv(self.aluguel_mensal + parcela),
                    self._decimal_csv(saldo),
                ])

    @staticmethod
    def _decimal_csv(valor: Decimal) -> str:
        return f"{dinheiro(valor):.2f}".replace(".", ",")


def ler_opcao(pergunta: str, opcoes: set[str]) -> str:
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in opcoes:
            return resposta
        print(f"Opção inválida. Escolha: {', '.join(sorted(opcoes))}.")


def ler_inteiro(pergunta: str, minimo: int, maximo: int | None = None) -> int:
    while True:
        resposta = input(pergunta).strip()
        try:
            valor = int(resposta)
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if valor >= minimo and (maximo is None or valor <= maximo):
            return valor
        if maximo is None:
            print(f"Digite um valor igual ou maior que {minimo}.")
        else:
            print(f"Digite um valor entre {minimo} e {maximo}.")


def criar_imovel() -> Imovel:
    print("\nTipos de imóvel:")
    print("1) Apartamento")
    print("2) Casa")
    print("3) Estúdio")
    tipo = ler_opcao("Escolha o tipo (1-3): ", {"1", "2", "3"})
    if tipo == "1":
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        criancas = ler_opcao("Possui crianças? (s/n): ", {"s", "n"}) == "s"
        garagem = ler_opcao("Deseja vaga de garagem por R$ 300,00/mês? (s/n): ", {"s", "n"}) == "s"
        return Apartamento(quartos, criancas, garagem)
    if tipo == "2":
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        garagem = ler_opcao("Deseja vaga de garagem por R$ 300,00/mês? (s/n): ", {"s", "n"}) == "s"
        return Casa(quartos, garagem)
    vagas = ler_inteiro("Quantidade de vagas (mínimo 2): ", 2)
    return Estudio(vagas)


def main() -> None:
    print("RentSmart — Orçamento de locação da R.M. Imóveis")
    imovel = criar_imovel()
    parcelas = ler_inteiro("Em quantas parcelas (1 a 5) deseja pagar a taxa contratual de R$ 2.000,00? ", 1, 5)
    orcamento = Orcamento(imovel, parcelas)
    orcamento.exibir_resumo()
    destino = Path("projecao_rentsmart.csv")
    orcamento.gerar_projecao_csv(destino)
    print(f"Projeção dos próximos 12 meses salva em: {destino.resolve()}")


if __name__ == "__main__":
    main()
