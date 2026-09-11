<p align="center">
  <img src="../../assets/logo.svg" alt="tldr" width="150" />
</p>

<h1 align="center">tldr</h1>

<p align="center">
  <strong>長すぎて読んでない —— AI コーディングエージェント向け。</strong>
</p>

<p align="center">
  エージェントは答えを 4 段落の奥に埋めてしまう。<br/>
  これは最初の 3 行に答えを出させ、残りを折りたたむ。<br/>
  <em>消すのではなく、下げる。</em>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <strong title="日本語">🇯🇵</strong>
</p>

---

## インストール

この一文をエージェントに貼り付けるだけです。Claude Code、Cursor、Codex、Gemini CLI などすべてで動きます。

```text
Install the tldr skill from https://github.com/SurefireStudios/tldr — read the repo's AGENTS.md for instructions.
```

コマンドで入れる場合（Claude Code）:

```bash
claude plugin marketplace add SurefireStudios/tldr
claude plugin install tldr@tldr
```

その他のエージェント: 🔗 **[INSTALL.md](../../INSTALL.md)**

そのあと `/tldr` と入力します。

## 何が問題か

問題は 2 つあります。

**エージェントが人間に話しすぎる。** はい・いいえで答えられる質問をしたのに、4 段落と番号付きの手順、エッジケースの注意書き、そして「お役に立てば幸いです！」が返ってくる。答えはそのどこかに埋まっています。

**エージェント同士も話しすぎる。** サブエージェントが検索を終え、3 行あれば足りるオーケストレーターに 4,000 トークンの説明を返す。その分は二重に払っています。生成時に一度、そしてセッションの残り全部でコンテキストを占有し続ける分でもう一度。

「簡潔に」系のプロンプトの多くは、**情報を削る**ことで 1 つ目の問題を解きます。コードレビューやセキュリティ監査など、後で責任を問われる作業では割に合いません。

## 消すのではなく、下げる

`tldr` はエージェントの発話量を減らすのではなく、**重要な部分を先に**言わせ、それ以外をすぐ下に置かせます。

何も捨てません。深さは利用者が決めます。

```markdown
**TL;DR**
- `listOrders` が行ごとに顧客テーブルを引いている: 1 ページの描画に 241 往復。
- 修正: `src/orders/repository.ts:88` で `include: { customer: true }` を渡し、下のループを削除する。
- 約 10 分。注文のベンチマークがこの経路をすでにカバーしている。

<details>
<summary>詳細</summary>

……エージェントが本来書いていた内容が、そのまま全部……

</details>
```

`<details>` が描画されないターミナルでは、代わりに `--- detail ---` という区切り線を使います。スキル自身がその違いを理解しています。

## 深さのダイヤル

折りたたみの上に何行出すかは利用者が決めます。

| コマンド | 結果 |
| --- | --- |
| `/tldr 0` | 見出しのみ。1 行、詳細なし。 |
| `/tldr 1` | 1 行 + 詳細。 |
| `/tldr 3` | **既定。** 3 行 + 詳細。 |
| `/tldr 5` | 5 行 + 詳細。 |
| `/tldr full` | オフ。通常に戻る。 |

ダイヤルは要約の長さだけを変えます。詳細が痩せることはありません。

## `/tldr` は動詞でもある

モードとして常時オンにもできますし、特定の対象に一度だけ使うこともできます。

```text
/tldr this file
/tldr that stack trace
/tldr the last 20 commits
/tldr your last answer
```

一回限りで、モードは変わりません。

## エージェント間: コストが効くところ

ここが、他の出力スタイル系スキルが扱っていない半分です。

出力先が人間ではなく**別のエージェント**のとき、`tldr` は解析可能なブロックに切り替わります。サブエージェントの報告、タスク結果、引き継ぎ、コミットメッセージ、PR 本文など:

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

効いているのは 3 つのルールです。

1. **ブロックを返して終える。** オーケストレーターが求めたのは結果であって、経過ではありません。
2. **長い版はファイルに書き、パスだけ返す。** コンテキストウィンドウに流し込まない。
3. **呼び出し側が逐語で必要とするものは圧縮しない** —— 正確なエラー、正確な diff、正確なパス。

## 決して圧縮しないもの

圧縮は文章には安全ですが、結果には安全ではありません。以下は常に折りたたみの上に、完全な形で出ます。

- 破壊的な操作 —— `rm -rf`、force push、テーブル削除、マイグレーション
- セキュリティ上の指摘 —— 折りたたまれた脆弱性は、報告されていない脆弱性
- 不可逆な操作とデータ損失
- 費用、クォータ、レート制限
- 貼り付けたり検索したりする必要のあるエラー原文
- 変更中のコードの diff —— 圧縮された diff は嘘
- 法務・医療・安全に関する境界
- 利用者が明示的に「全部見せて」と言ったもの

スキル自身の言葉で言えば: **TL;DR だけを読んだ人が、誤った理解に至ってはならない。**

## 本当に効果はあるのか

[`evals/`](../../evals/) に再現可能な評価ハーネスがあり、ふつうは一緒に測られない 2 つを同時に測ります。

- **品質** —— 正確性、忠実性、実行可能性、安全性を、ベースラインに対してブラインドで採点。
- **トークン** —— 実際の出力トークン数。圧縮の目的はコストだからです。

どちらか片方だけを出すことが、圧縮に関する主張が誤解を招く典型的な経路です。手法とリリース基準は [`evals/RESULTS.md`](../../evals/RESULTS.md) にあります。数字はスキルに有利かどうかに関わらず公開します。

## 対応エージェント

Claude Code、Cursor、Codex、Gemini CLI、GitHub Copilot、OpenCode、Zed、Windsurf、Cline、Roo Code、Aider、Amp、Qwen Code、Kimi Code CLI、Pi、Oh My Pi、Antigravity —— 詳しい手順は [INSTALL.md](../../INSTALL.md) にあります。

スキル自体はランタイム不要の素の markdown なので、カスタム指示を受け付けるツールなら一覧にないものでも動きます。

## ライセンス

MIT。

---

<p align="center">
  <strong>TL;DR: スターを。⭐</strong><br/>
  <sub>「長いものは読まない」ための README を、最後まで読んでしまいましたね。<br/>
  最後のワンクリックまで面倒がらずに。</sub>
</p>
