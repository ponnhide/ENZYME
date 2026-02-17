# ENZYME v7: 生命科学プロトコル形式化の実証評価（論文調レポート）

## 要旨
本研究は、自然言語で記述された生命科学プロトコルを、検証可能な計算表現へ変換し、再現性を定量評価するためのENZYMEフレームワークを評価した。
Nat Protocols 14報とNat siblings 20報（計34報）を対象に、gpt-oss-120b-v7 と qwen3-next-80b-a3b-instruct-fp8-v7 の2モデルで全件処理を行い、形式化品質（total）と再現性指標（repro）を比較した。
両モデルで protocols > siblings の傾向が再現され、qwen3-next-80b-a3b-instruct-fp8-v7 では repro 群差が有意（Mann-Whitney p=0.031225）となった。
結果は、ENZYMEが手順知識を『実行可能な表現』へ落とし込み、文献比較を再現可能な計量として扱えることを示す。

## 1. 背景と問題設定
生命科学の方法記述は情報量が高い一方、機械的な比較・監査・再利用には依然として不向きである。
QUEENは、DNA構築プロセスをコードとして再構成し、配列だけでなく構築履歴まで再生成可能にすることで、透明性と追跡可能性を高めた。ENZYMEはこの思想をプロトコル表現へ拡張し、『何をどの順序で、どの条件で行ったか』を、検証・採点可能なIRとして定義することを狙う。

## 2. ENZYMEの設計思想
### 2.1 コア関数（Core-IR）
Core-IRは `allocate` / `transfer` / `manipulate` / `run_device` / `observe` / `annotate` / `dispose` を中心演算とする。
この最小集合は、実験ドメイン固有の語彙差を吸収しつつ、フロー検証とスコアリングを共通化するための設計である。
### 2.2 形式化戦略（HL-Core と Direct-Core）
ENZYMEは HL-IR→Lowering→Core-IR の段階変換と、LLMが直接Coreを出力する direct-core の両方を許容する。
Lowering では、`measure` を `run_device` + `observe` に分解し、内部データ参照（例: raw readout）を明示して、観測ステップへの依存関係を保存する。
### 2.3 スコアリング
default score（total）は9成分（構造、語彙、パラメータ、識別、実行環境、曖昧性、手順性、特異性、カバレッジ）の等重み平均。
repro score は profile 駆動で資材識別・装置識別・パラメータ完全性・QC・トレーサビリティ等を評価し、MVP方針として `total_mode=equal_average_non_flow`（非flowカテゴリの等重み）を採用する。
flowは重み合算ではなく viability gate として扱い、重大なフロー不整合を再現性リスクとして明示する。
### 2.4 Flow評価
unit間接続は strictな material_flow（参照ID一致）と heuristicな logical_flow（時系列窓・語彙アンカー・継続句）を併用し、combined_integrity で孤立unit率を報告する。

## 3. 評価設定
- コーパス: nat_protocols 14報、nat_siblings 20報（計34報）
- モデル: `gpt-oss-120b-v7`, `qwen3-next-80b-a3b-instruct-fp8-v7`
- 各runは全件完走し、paper欠損スコアは0
- バイオセーフティ配慮のため、具体的な実験手順や条件は本報告に記載しない

## 4. 結果
### 4.1 実行完全性
- gpt-oss-120b-v7: papers=34, units=228, failures=0, missing_total=0, missing_repro=0
- qwen3-next-80b-a3b-instruct-fp8-v7: papers=34, units=231, failures=0, missing_total=0, missing_repro=0
### 4.2 paper平均スコア

| model | group | total_mean | repro_mean |
|---|---:|---:|---:|
| gpt-oss-120b-v7 | nat_protocols | 75.035 | 27.239 |
| gpt-oss-120b-v7 | nat_siblings | 72.126 | 23.188 |
| qwen3-next-80b-a3b-instruct-fp8-v7 | nat_protocols | 72.836 | 25.814 |
| qwen3-next-80b-a3b-instruct-fp8-v7 | nat_siblings | 66.691 | 19.065 |

- wins(total, gpt-oss-120b-v7 vs qwen3-next-80b-a3b-instruct-fp8-v7): 28/5/tie 1
- wins(repro, gpt-oss-120b-v7 vs qwen3-next-80b-a3b-instruct-fp8-v7): 19/14/tie 1
### 4.3 repro群差の統計
- gpt-oss-120b-v7: MWU p=0.096380, Welch p=0.089538, Cohen d=0.537, Cliff delta=0.343
- qwen3-next-80b-a3b-instruct-fp8-v7: MWU p=0.031225, Welch p=0.003886, Cohen d=0.978, Cliff delta=0.443
### 4.4 モデル間相関
- all: n=34, pearson_total=0.467, pearson_repro=0.355
- nat_protocols: n=14, pearson_total=0.420, pearson_repro=0.001
- nat_siblings: n=20, pearson_total=0.400, pearson_repro=0.313
### 4.5 フロー・カテゴリ
- gpt-oss-120b-v7/nat_protocols: combined_pass_rate=0.571, combined_isolated_rate_mean=0.095, corr(repro, connectivity)=0.055
- gpt-oss-120b-v7/nat_siblings: combined_pass_rate=0.100, combined_isolated_rate_mean=0.522, corr(repro, connectivity)=-0.062
- qwen3-next-80b-a3b-instruct-fp8-v7/nat_protocols: combined_pass_rate=0.500, combined_isolated_rate_mean=0.094, corr(repro, connectivity)=0.385
- qwen3-next-80b-a3b-instruct-fp8-v7/nat_siblings: combined_pass_rate=0.350, combined_isolated_rate_mean=0.418, corr(repro, connectivity)=0.669

## 5. 議論
### 5.1 ENZYMEが示した価値
第一に、文献方法記述を機械可読IRへ変換し、比較可能な数量へ落とし込む基盤が実働した。
第二に、単一スコアではなく、構造・語彙・パラメータ・flow・カテゴリ分布を分離計測でき、『何が再現性のボトルネックか』を診断可能にした。
### 5.2 QUEEN思想との接続
QUEENがDNA構築履歴の再生成可能性を通じて透明性を高めたのに対し、ENZYMEは実験プロトコルの実行記述を関数型IRとして正規化し、検証・採点・横断比較を可能にする。
両者に共通する核は、『自然言語叙述を再構成可能な計算表現へ写像する』という方法論である。
### 5.3 限界
- logical_flow は語彙ヒューリスティック依存で、意味依存の誤連結/未連結余地がある。
- unit分割品質は上流抽出の影響を受ける。
- 現時点では2モデル比較であり、モデル多様性の拡張が必要。
### 5.4 今後の発展
- logical_flowを学習ベースまたは検証器付き推論へ拡張し、説明可能性を維持したまま精度向上。
- 大規模コーパス（Nat Protocols全体）へ適用し、分野別の再現性地図を構築。
- profile項目の寄与を事後推定し、重み設計をデータ駆動で更新。
- QUEEN的なトレーサビリティ思想と接続し、実験設計-実施-報告の循環を閉じる。

## 6. 結論
ENZYME v7全件評価は、生命科学プロトコルの形式化と再現性計量に関して、実運用可能なパイプラインが成立していることを示した。
特に、protocols/siblingsの群差、flow指標、カテゴリ構造を一体で扱える点は、従来の定性的読解では得にくい比較軸を提供する。
今後は、精度改善（flow・segmentation）と適用規模拡大により、生命科学Methodsの客観的監査基盤としての意義をさらに高められる。

## 参考文献
1. Yachie et al., Nature Communications (2022), QUEEN framework. https://www.nature.com/articles/s41467-022-30588-x
2. ENZYME Spec v0.4 (`ENZYME_Spec_v0_4.md`)
