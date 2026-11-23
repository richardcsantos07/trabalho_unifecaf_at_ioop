# RentSmart

Trabalho da disciplina **Algorithmic Thinking & Introduction to Object-Oriented Programming** (UniFecaf). O RentSmart calcula orçamentos de locação para a R.M. Imóveis, explica cada componente do preço e salva a projeção dos primeiros 12 meses em CSV.

## Requisitos

- Python 3.10 ou superior
- Nenhuma dependência externa

## Como executar

No terminal, dentro da pasta do projeto:

```bash
python rent_smart.py
```

Responda às perguntas. O programa valida as opções e cria `projecao_rentsmart.csv` na pasta atual. O CSV usa `;` como separador e vírgula decimal para facilitar a abertura em planilhas configuradas para português.

## Regras implementadas

- Apartamento de 1 quarto: R$ 700,00; 2 quartos: adicional de R$ 200,00.
- Casa de 1 quarto: R$ 900,00; 2 quartos: adicional de R$ 250,00.
- Apartamento e casa: vaga opcional por R$ 300,00 mensais.
- Apartamento sem crianças: desconto de 5% sobre o subtotal após os adicionais.
- Estúdio: aluguel de R$ 1.200,00; pacote inicial de 2 vagas por R$ 250,00; cada vaga além das duas custa R$ 60,00.
- Taxa contratual separada do aluguel: R$ 2.000,00, em 1 a 5 parcelas.
- O CSV discrimina aluguel, parcela contratual, total previsto e saldo da taxa em cada mês. Quando a taxa termina, o total mensal volta a ser apenas o aluguel.

## Organização orientada a objetos

- `Imovel` define a interface comum dos imóveis.
- `Apartamento`, `Casa` e `Estudio` implementam os adicionais específicos de cada categoria.
- `Orcamento` concentra desconto, aluguel mensal, parcelamento, resumo e exportação CSV.
- Funções de entrada ficam separadas das regras de negócio e validam as respostas do usuário.

## Arquivos da entrega

- `rent_smart.py`: aplicação executável.
- `documentacao_teorica.md` e `documentacao_teorica.pdf`: análise, entradas/processamentos/saídas, fluxograma e justificativa da solução.
- `roteiro_pitch.md`: roteiro sugerido para o vídeo de até 4 minutos.
- `gerar_pdf.py`: gerador do PDF usando apenas a biblioteca padrão do Python.

## Repositório e vídeo pitch

Repositório configurado para o projeto: [github.com/richardcsantos07/trabalho_unifecaf_at_ioop](https://github.com/richardcsantos07/trabalho_unifecaf_at_ioop). Os arquivos preparados nesta pasta ainda precisam ser enviados ao remoto pelo titular da conta. O vídeo pitch também precisa ser gravado e publicado pelo estudante; o roteiro está em `roteiro_pitch.md`.
