# GitHub Workflows

このディレクトリには GitHub Actions ワークフローが含まれています。

## Pomodoro Documentation Sync ワークフロー（削除済み）

`pomodoro-docs-sync` ワークフローは一時的に削除されました。このワークフローは `1.pomodoro/` 配下のコード変更を検出し、ドキュメントを自動更新する機能を提供していましたが、必要なシークレットが設定されていないため動作しませんでした。

### 再度有効化する場合

このワークフローを再度有効化するには:

1. **COPILOT_GITHUB_TOKEN シークレットの設定**
   - リポジトリの Settings > Secrets and variables > Actions に移動
   - "New repository secret" をクリック
   - Name: `COPILOT_GITHUB_TOKEN`
   - Value: GitHub Copilot CLI の認証トークン
   - 詳細: https://github.github.com/gh-aw/reference/engines/#github-copilot-default

2. **ワークフローファイルの復元**
   - Git の履歴から `pomodoro-docs-sync.md` と `pomodoro-docs-sync.lock.yml` を復元
   - または、新しいワークフローを gh-aw で作成

3. **ドキュメントディレクトリの準備**
   - `1.pomodoro/docs/` ディレクトリを作成
   - 初期ドキュメントファイルを配置

## その他の注意事項

- `.lock.yml` ファイルは自動生成されるため、直接編集しないでください
- ワークフローを変更する場合は `.md` ファイルを編集し、`gh aw compile` を実行してください
