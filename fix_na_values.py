import pandas as pd
import json
import os
import glob
from pathlib import Path

def fix_na_values():
    # Загружаем текущий CSV
    csv_files = glob.glob("results/evaluations_summary_*.csv")
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"📂 Загружаем: {latest_csv}")
    
    df = pd.read_csv(latest_csv)
    
    # Находим строки с N/A
    na_rows = df[df['final_score'].isna()]
    print(f"\n🔍 Найдено {len(na_rows)} строк с N/A")
    
    if len(na_rows) == 0:
        print("✅ Все оценки есть!")
        return
    
    # Ищем partial файлы
    partial_files = glob.glob("results/partial_eval_*.json")
    print(f"📁 Найдено partial файлов: {len(partial_files)}")
    
    # Собираем все сохраненные результаты
    all_results = []
    for pf in partial_files:
        with open(pf, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                all_results.extend(data)
            else:
                all_results.append(data)
    
    print(f"📊 Всего записей в partial файлах: {len(all_results)}")
    
    # Создаем словарь для быстрого поиска
    results_dict = {}
    for r in all_results:
        key = f"{r.get('segment_id')}_{r.get('translation_engine')}"
        results_dict[key] = r
    
    # Восстанавливаем оценки
    fixed_count = 0
    for idx, row in na_rows.iterrows():
        key = f"{row['segment_id']}_{row['engine']}"
        if key in results_dict:
            mod_eval = results_dict[key].get('moderator_evaluation', {})
            if isinstance(mod_eval, dict):
                if 'final_score' in mod_eval:
                    df.at[idx, 'final_score'] = mod_eval['final_score']
                    df.at[idx, 'expert_agreement'] = mod_eval.get('expert_agreement', 'частичное')
                    fixed_count += 1
                    print(f"  ✓ Восстановлен {key}: {mod_eval['final_score']}")
    
    print(f"\n✅ Восстановлено {fixed_count} из {len(na_rows)} оценок")
    
    # Сохраняем исправленный файл
    output_file = latest_csv.replace('.csv', '_fixed.csv')
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"💾 Сохранено в: {output_file}")

if __name__ == "__main__":
    fix_na_values()