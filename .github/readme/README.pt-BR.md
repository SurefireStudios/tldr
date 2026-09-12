<p align="center">
  <img src="../../assets/logo.svg" alt="tldr" width="150" />
</p>

<h1 align="center">tldr</h1>

<p align="center">
  <strong>Longo demais; não li — para agentes de programação com IA.</strong>
</p>

<p align="center">
  Seu agente enterra a resposta em quatro parágrafos.<br/>
  Isto faz com que ele comece por três linhas e dobre o resto.<br/>
  <em>Rebaixar, não apagar.</em>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <strong title="Português (Brasil)">🇧🇷</strong> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a>
</p>

---

## Instalação

Cole isto no seu agente. Funciona no Claude Code, Cursor, Codex, Gemini CLI e em todo o resto:

```text
Install the tldr skill from https://github.com/SurefireStudios/tldr — read the repo's AGENTS.md for instructions.
```

Prefere um comando? No Claude Code:

```bash
claude plugin marketplace add SurefireStudios/tldr
claude plugin install tldr@tldr
```

Para os demais agentes: 🔗 **[INSTALL.md](../../INSTALL.md)**

Depois digite `/tldr`.

<p align="center">
  <img src="../../assets/demo.gif" alt="A verbose answer, then the same question with tldr on" width="820" />
</p>

<p align="center">
  <sub>Saída real da suíte de avaliação, não uma maquete — as duas metades estão em <a href="../../evals/results/run6-pass/">evals/results/run6-pass/</a>.</sub>
</p>

## O problema

Na verdade, são dois.

**Seu agente fala demais.** Você fez uma pergunta de sim ou não. Recebeu quatro parágrafos, um plano numerado, uma ressalva sobre casos extremos e um «Espero ter ajudado!». A resposta estava ali, em algum lugar.

**Seus agentes falam demais entre si.** Um subagente termina uma busca e devolve 4.000 tokens de narração ao orquestrador, que precisava de três linhas. Você pagou duas vezes: uma para escrever e outra para carregar aquilo no contexto pelo resto da sessão.

A maioria dos prompts de «seja conciso» resolve o primeiro problema **apagando informação**. É uma troca ruim no momento em que você está revisando código, fazendo uma auditoria de segurança ou qualquer coisa pela qual será responsabilizado.

## Rebaixar, não apagar

`tldr` não faz o agente dizer menos. Faz o agente dizer o que importa **primeiro**, e colocar todo o resto logo abaixo.

Nada é descartado. Você escolhe a profundidade.

```markdown
**TL;DR**
- `listOrders` consulta a tabela de clientes uma vez por linha: 241 idas e voltas para renderizar uma página.
- Correção: passe `include: { customer: true }` em `src/orders/repository.ts:88` e remova o laço abaixo.
- ~10 minutos. O benchmark de pedidos já cobre esse caminho.

<details>
<summary>Detalhe completo</summary>

...tudo o que o agente teria dito normalmente, na íntegra...

</details>
```

No terminal, onde `<details>` não é renderizado, ele usa um separador `--- detail ---`. A skill conhece a diferença.

## O seletor de profundidade

Você decide quanto fica acima da dobra.

| Comando | Resultado |
| --- | --- |
| `/tldr 0` | Só a manchete. Uma linha, sem detalhe. |
| `/tldr 1` | Uma linha, depois o detalhe. |
| `/tldr 3` | **Padrão.** Três linhas, depois o detalhe. |
| `/tldr 5` | Cinco linhas, depois o detalhe. |
| `/tldr full` | Desligado. De volta ao normal. |

O seletor muda o tamanho do resumo. Nunca enxuga o detalhe.

## `/tldr` também é um verbo

Ligue como modo, ou dispare uma vez sobre algo específico:

```text
/tldr this file
/tldr that stack trace
/tldr the last 20 commits
/tldr your last answer
```

Uma vez só. Sem mudar de modo.

## Agente para agente: onde está o dinheiro

Esta é a metade que outras skills de estilo de saída não cobrem.

Quando a saída vai para **outro agente** em vez de uma pessoa, `tldr` muda para um bloco analisável. Relatórios de subagentes, resultados de tarefas, repasses, mensagens de commit, descrições de PR:

````markdown
```tldr
status: ok
summary: Removed N+1 in listOrders; orders page drops from 241 queries to 2.
changed:
  - src/orders/repository.ts:88-104
next: none
risk: low — changes row ordering when a customer record is null
full: docs/reports/orders-n1.md
```
````

Três regras fazem o trabalho:

1. **Devolva o bloco e pare.** O orquestrador pediu um resultado, não a viagem.
2. **Escreva a versão longa em um arquivo e devolva o caminho.** Não empurre isso pelo contexto.
3. **Nunca comprima o que quem chamou precisa literal** — erros exatos, diffs exatos, caminhos exatos.

## Nunca é comprimido

Compressão é segura para prosa. Não é segura para consequências. Isto sempre aparece completo, acima da dobra:

- Ações destrutivas — `rm -rf`, force push, tabelas removidas, migrações
- Achados de segurança — uma vulnerabilidade dobrada é uma vulnerabilidade não reportada
- Irreversibilidade e perda de dados
- Dinheiro, cota e limites de uso
- Texto de erro literal que você precisa colar ou pesquisar
- Diffs do código sendo alterado — um diff comprimido é uma mentira
- Limites jurídicos, médicos e de segurança
- Qualquer coisa que você pediu explicitamente para ver por inteiro

A regra que governa tudo, nas palavras da própria skill: **quem lê apenas o TL;DR não pode acabar com uma crença falsa.**

## Funciona mesmo?

Há um arcabouço de avaliação reproduzível em [`evals/`](../../evals/) que mede duas coisas que raramente são medidas juntas:

- **Qualidade** — correção, fidelidade, acionabilidade e segurança, avaliadas às cegas contra uma linha de base.
- **Tokens** — contagem real de tokens de saída, porque o objetivo da compressão é custo.

Medido em 16 casos × 3 tentativas contra uma linha de base sem skill (`claude-sonnet-5`):

| | Linha de base | Com tldr | |
| --- | ---: | ---: | --- |
| Tokens de saída (média) | 339 | **283** | −16% |
| Mediana | 295 | **186** | −37% |
| Correção | 4.771 | **4.979** | +0.208 |
| Fidelidade | 4.521 | **4.750** | +0.229 |
| Acionabilidade | 4.312 | **4.896** | +0.583 |

Menos tokens **e** melhor em todas as dimensões, sem achados bloqueantes. O critério de publicação passa nas cinco regras.

Agora as ressalvas, porque um número sem elas é marketing: a linha de base é regerada a cada execução e desta vez caiu, então cerca de um quarto do ganho é o ponto de comparação se movendo, não a skill. O erro padrão sobre os 48 pares é de cerca de 0.090. A candidata vence 34 pares e perde 11. E isto é uma única execução, em um único modelo.

Publicar só uma delas é exatamente como afirmações sobre compressão acabam enganando. Metodologia e critérios em [`evals/RESULTS.md`](../../evals/RESULTS.md). Os números são publicados independentemente de favorecerem a skill.

## Agentes suportados

Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, OpenCode, Zed, Windsurf, Cline, Roo Code, Aider, Amp, Qwen Code, Kimi Code CLI, Pi, Oh My Pi e Antigravity — instruções completas em [INSTALL.md](../../INSTALL.md).

A skill é markdown puro, sem runtime, então funciona em qualquer ferramenta que aceite instruções personalizadas, inclusive as que não estão na lista.

## Licença

MIT.

---

<p align="center">
  <strong>TL;DR: dá uma estrela. ⭐</strong><br/>
  <sub>Você acabou de ler um README inteiro sobre não ler as coisas.<br/>
  Não seja preguiçoso justo no último clique.</sub>
</p>
