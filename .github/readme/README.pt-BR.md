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
| `/tldr brief` | Segura o detalhe até você pedir. Combina com qualquer profundidade. |

O seletor muda o tamanho do resumo. Nunca enxuga o detalhe.

### Modo breve

`<details>` só dobra onde o HTML é renderizado. No terminal, e em alguns apps de chat, não há triângulo para clicar: a resposta completa chega como um bloco, por menor que seja o resumo.

`/tldr brief` é a dobra que essas superfícies não conseguem desenhar. O TL;DR aparece; o detalhe espera. Diga `more` e você recebe o detalhe na íntegra, não uma versão encurtada. `/tldr detail` desliga.

O que ele nunca faz: **segurar qualquer coisa da lista de "nunca comprimir"**. Comandos destrutivos, achados de segurança, custo, erros literais e diffs aparecem na própria resposta breve. Um achado de segurança segurado é um achado não reportado.

## `/tldr` também é um verbo

Ligue como modo, ou dispare uma vez sobre algo específico:

```text
/tldr this file
/tldr that stack trace
/tldr the last 20 commits
/tldr your last answer
```

Uma vez só. Sem mudar de modo.

## `tldr-write`: a mesma ideia, voltada para fora

`tldr` molda o que um agente diz **para você**, e nos casos que importam ele fica *mais longo*, porque para de afinar as ressalvas.

`tldr-write` molda o que você envia **para outra pessoa**: um e-mail, uma resposta no Slack, a descrição de um PR, um comentário de revisão, uma mensagem de commit. Outro trabalho, resultado oposto:

```
Antes    Oi pessoal! Espero que todos tenham tido um ótimo fim de semana. Queria
         retomar a discussão sobre cache que tivemos na terça passada. Como vocês
         devem lembrar, estávamos debatendo entre Redis e cache em processo para o
         armazenamento de sessões. Pesquisei um pouco e acho que, pela minha
         análise, o Redis é provavelmente a melhor opção, principalmente porque
         rodamos quatro servidores de aplicação e com cache em processo a sessão de
         um usuário pode cair num servidor que não a tem. Enfim, me digam o que
         acham! Obrigado!

Depois   Recomendo o Redis para o armazenamento de sessões: rodamos quatro
         servidores de aplicação, e com cache em processo a sessão de um usuário
         pode cair num que não a tem.
```

O pedido vem primeiro. O preâmbulo, a pergunta repetida, os rodeios e o "espero ter ajudado!" somem. Mas **curto não é o mesmo que seco**, e uma lista do que nunca se corta segura a linha: o pedido e o prazo, o bloqueio e quem o detém, a ressalva que mudaria a decisão, o crédito com nomes, o pedido de desculpas se for devido, a má notícia cedo e sem rodeios, o custo e o irreversível.

Ligue com `/tldr-write`, ou use uma vez só: `/tldr-write esta descrição de PR`.

### Por que tem a própria rubrica

`tldr` podia trapacear apagando, então sua avaliação pesa fidelidade em 25%.

A trapaça desta skill é mais barata. `"Não."` é mais curto que `"Essa semana não dá — estou de plantão e liberando na quinta. Sexta eu leio direito, se ajudar."` As duas recusam, as duas são exatas, e em todas as dimensões que a primeira rubrica mede a grosseira vence.

Por isso esta suíte pontua **adequação em 20%** e a exige no critério de publicação: *a pessoa que recebe isso se sentiria respeitada?* Um candidato mais frio que a linha de base não é publicado, por menos tokens que use.

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Correção | 4.479 → **4.854** | +0.375 | 3.521 → **4.771** | **+1.250** |
| Fidelidade | 4.833 → **4.833** | +0.000 | 4.917 → **4.896** | −0.021 |
| Adequação | 4.083 → **4.375** | +0.292 | 4.333 → **4.688** | +0.354 |
| Acionabilidade | 3.458 → **4.958** | +1.500 | 4.104 → **4.979** | +0.875 |
| Concisão | 2.646 → **4.896** | +2.250 | 2.625 → **4.938** | +2.312 |
| Tokens de saída | 226 → **87** | **−61%** | 373 → **124** | **−67%** |

Passa nas cinco regras nos dois modelos.

### O número que não é a contagem de tokens

A correção da linha de base no Opus, 3.521, é o menor valor de todo o arquivo de resultados, e tem uma causa só: **um modelo sem a skill inventa fatos quando redige uma mensagem por você.** 20 de 48 respostas base pontuam 3 ou menos, sempre pelo mesmo motivo.

O enunciado inteiro de um caso é: *"Subi uma migração às 16h que travou a tabela de pedidos por 20 minutos em horário comercial. O suporte atendeu umas 40 ligações. Escreva minha mensagem para o líder do suporte."*

O rascunho sem a skill:

> Já está resolvido — **nenhum dado foi perdido ou corrompido**, e **a fila esvaziou assim que o lock foi liberado**. **Quem tentou de novo depois das 16h20 deve ter passado normalmente.** […] **migrações assim passam a sair fora do horário comercial**

Quatro coisas que ninguém disse. Três são afirmações sobre um incidente em produção que você não consegue sustentar; a quarta te compromete com uma mudança de processo. E você ia enviar isso para um colega.

Datas inventadas no conjunto completo: Sonnet 6/48 → 1/48, **Opus 5/48 → 0/48**.

67% menos tokens é o número que cabe num slide. "Impede seu agente de escrever *nenhum dado foi perdido* num pedido de desculpas por incidente" é o que importa.

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

Medido em 16 casos × 3 tentativas, avaliado às cegas contra uma linha de base sem skill, em dois modelos com o mesmo instrumento. Esta é a skill publicada (v0.4.0):

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Correção | 4.896 → **4.938** | +0.042 | 4.708 → **4.875** | +0.167 |
| Fidelidade | 4.583 → **4.854** | +0.271 | 4.667 → **4.854** | +0.188 |
| Acionabilidade | 4.417 → **4.875** | +0.458 | 4.500 → **4.833** | +0.333 |
| Segurança | 4.458 → **4.750** | +0.292 | 4.542 → **4.896** | +0.354 |
| Tokens de saída agente-a-agente | 172 → **105** | −39% | 320 → **137** | −57% |
| Tokens de saída para humanos, média | 346 → 374 | +8% | 535 → 555 | +4% |
| Tokens da própria skill por turno (sempre ativa) | 4,380 → **1,078** | −75% | 4,380 → **1,078** | −75% |

Melhor em todas as dimensões, nos dois modelos, e **o critério de publicação passa nas cinco regras em ambos**. Leia as linhas de tokens com atenção: onde a skill comprime — relatórios agente-a-agente — a saída cai entre um terço e a metade. Onde ela se recusa a comprimir — ações destrutivas, achados de segurança, custo, erros — a saída fica mais longa, porque o modelo agora mantém cada ressalva acima da dobra em vez de afiná-la; é por isso que a média sobe, e cada um desses casos pontuou mais alto em fidelidade ou segurança. A mediana não é publicada aqui: entre duas execuções da mesma skill ela inverteu de sinal, então com 48 linhas não é um número estável. O maior número é o tamanho da própria skill: um harness sempre ativo a reenvia a cada turno, e a versão anterior de 18k custava cerca de 80 vezes por turno o que economizava.

Foram treze execuções, incluindo as que falharam e uma em que o erro estava no meu próprio harness. Metodologia, critérios e as treze em [`evals/RESULTS.md`](../../evals/RESULTS.md). Os números são publicados independentemente de favorecerem a skill.

## Agentes suportados

Claude Code, Cursor, Cybara, OpenClaw, Hermes, Codex, Gemini CLI, GitHub Copilot, OpenCode, Zed, Windsurf, Cline, Roo Code, Aider, Amp, Qwen Code, Kimi Code CLI, Pi, Oh My Pi e Antigravity — instruções completas em [INSTALL.md](../../INSTALL.md).

A skill é markdown puro, sem runtime, então funciona em qualquer ferramenta que aceite instruções personalizadas, inclusive as que não estão na lista.

## Licença

MIT.

---

<p align="center">
  <strong>TL;DR: dá uma estrela. ⭐</strong><br/>
  <sub>Você acabou de ler um README inteiro sobre não ler as coisas.<br/>
  Não seja preguiçoso justo no último clique.</sub>
</p>
