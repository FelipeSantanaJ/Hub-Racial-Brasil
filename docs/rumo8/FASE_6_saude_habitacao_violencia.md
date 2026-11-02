# Fase 6 — Saúde, habitação e violência (esforço alto; só depois de 1–5 aprovadas)

Decisão sua: "adicione tudo que der". Como seu projeto de conteúdo recomenda não abordar tudo ao mesmo tempo, esta fase produz **análise e ficha**, não conteúdo; a decisão editorial vem depois.

```text
FASE 6 — Saúde, habitação e violência. Branch: rumo8/fase6. Pré-requisito: Fases 1–5 aprovadas. IDs: SA*, HB*, VI*.

REGRA DE ENTRADA
Antes de qualquer resultado, cada tema tem uma ficha de QUALIDADE DO CAMPO RAÇA: completude (ignorados), mudança de preenchimento no tempo e por UF. Se o campo for inutilizável num recorte, o estudo daquele recorte fica "Bloqueado (por dado)".

SAÚDE
SA1 Mortalidade por raça (SIM): taxa padronizada por idade e sexo, com denominadores do Censo 2022 (público até UF) e projeções por raça apenas se houver fonte oficial [a confirmar]. Preste atenção ao viés de numerador x denominador (autodeclaração diferente nas duas fontes).
SA2 Mortalidade infantil e materna e pré-natal por raça (SINASC/SIM).
SA3 PNS (se houver corte por raça): acesso e autoavaliação de saúde. [a confirmar edições]
Perguntas do meio do caminho: a diferença de mortalidade é de composição etária/regional ou persiste? O campo raça melhora ao longo do tempo e isso cria tendência espúria?

HABITAÇÃO
HB1 Revisar o que já existe em agregacoes_habitacao.py (PNAD anual) com as regras 5 e 6.
HB2 Censo 2022 (domicílios, público até UF): água, esgoto, densidade, condição de ocupação por raça do responsável.
HB3 Ligar à riqueza imobiliária (H3.4) sem dupla contagem.
Perguntas: a diferença de saneamento é entre regiões ou dentro delas?

VIOLÊNCIA
VI1 Homicídio por raça, idade e UF (SIM), com a mesma regra de denominador; letalidade policial só se houver fonte oficial com raça [a confirmar].
VI2 Ligar à trilha EF5-R2 (jovens 15–29) com ressalva de que a ligação é descritiva.

ACEITE
- Ficha de qualidade do campo raça para cada fonte, antes dos resultados.
- Cada estudo com frases permitidas e proibidas; nenhum causal.
- Verificação independente de >= 5 números por tema.

GATE: relatório; você decide o que (se algo) vira conteúdo.
```

---
