# Pipeline QSPR reutilizavel

## Fluxo
1. `pubchem_smiles_scraper.py` (opcional): adiciona `SMILES` ao CSV base.
2. `index_calculation.py`: calcula indices topologicos a partir de `SMILES`.
3. `merge_target_and_indices.py`: junta propriedades + indices.
4. `clean_data_for_qspr.py`: normaliza colunas numericas.
5. `qspr.py`: roda regressao QSPR (1 propriedade vs 1 indice).

## Execucao em um comando

Use `run_pipeline.py` para executar tudo:

```bash
python run_pipeline.py targets_article.csv
```

Se o arquivo `targets_article_with_smiles.csv` existir no mesmo diretorio, ele sera usado automaticamente para calcular indices.

Se quiser definir explicitamente o arquivo com SMILES:

```bash
python run_pipeline.py targets_article.csv --smiles-source-csv targets_article_with_smiles.csv
```

Para ja gerar o pacote de apresentacao do capitulo 5:

```bash
python run_pipeline.py targets_article.csv \
  --smiles-source-csv targets_article_with_smiles.csv \
  --chapter5-report --chapter5-min-r2 0.4 --chapter5-top-k 3
```

## Reutilizacao com outro CSV base

Exemplo com nova base:

```bash
python run_pipeline.py minha_base.csv --smiles-source-csv minha_base_with_smiles.csv
```

## Scripts individuais

Calcular indices:

```bash
python index_calculation.py minha_base_with_smiles.csv -o indices.csv --drug-column Drug --smiles-column SMILES
```

Merge:

```bash
python merge_target_and_indices.py minha_base.csv indices.csv -o merged.csv
```

Limpeza:

```bash
python clean_data_for_qspr.py merged.csv -o clean.csv
```

QSPR:

```bash
python qspr.py clean.csv -o qspr_results.csv
```

## Apresentacao estilo Capitulo 5

Depois de gerar `*_qspr_results.csv` e `*_qspr_clean.csv`, gere o pacote de apresentacao:

```bash
python chapter5_report.py targets_article_qspr_results.csv targets_article_qspr_clean.csv
```

Saidas principais:
- `chapter5_all_models.csv`
- `chapter5_top_models_per_property.csv`
- `chapter5_best_models.csv`
- `chapter5_best_model_predictions.csv`
- `chapter5_r2_matrix.csv`
- `chapter5_pvalue_matrix.csv`
- `chapter5_equations_by_index.csv`
- `chapter5_equations_by_index.md`
- `chapter5_tables_3_to_12.csv`
- `chapter5_tables_3_to_12.md`
- `chapter5_report.md`
