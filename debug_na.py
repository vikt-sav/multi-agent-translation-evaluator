import pandas as pd
import json
import glob
import os
from collections import Counter

def debug_na():
    print("🔍 ДИАГНОСТИКА ПРОПУЩЕННЫХ ЗНАЧЕНИЙ")
    print("="*60)
    
    # 1. Загружаем CSV с N/A
    csv_files = glob.glob("results/evaluations_summary_*.csv")
    latest_csv = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest_csv)
    
    na_rows = df[df['final_score'].isna()]
    print(f"\n📊 CSV файл: {latest_csv}")
    print(f"Всего строк: {len(df)}")
    print(f"Строк с N/A: {len(na_rows)}")
    
    print("\n🔢 Строки с N/A (segment_id, engine):")
    na_keys = []
    for _, row in na_rows.iterrows():
        key = f"{row['segment_id']}_{row['engine']}"
        na_keys.append(key)
        print(f"  - {key}")
    
    # 2. Анализируем partial файлы
    partial_files = glob.glob("results/partial_eval_*.json")
    print(f"\n📁 Найдено partial файлов: {len(partial_files)}")
    
    # Смотрим структуру первого partial файла
    if partial_files:
        with open(partial_files[0], 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        print("\n📋 СТРУКТУРА PARTIAL ФАЙЛА (пример):")
        if isinstance(sample_data, list) and len(sample_data) > 0:
            first = sample_data[0]
            print(f"Тип данных: список из {len(sample_data)} элементов")
            print(f"Ключи в первом элементе: {list(first.keys())}")
            
            # Проверяем, есть ли нужные поля
            if 'segment_id' in first:
                print(f"  ✓ segment_id: {first['segment_id']}")
            if 'translation_engine' in first:
                print(f"  ✓ translation_engine: {first['translation_engine']}")
            if 'moderator_evaluation' in first:
                print(f"  ✓ moderator_evaluation присутствует")
                mod_eval = first['moderator_evaluation']
                if isinstance(mod_eval, dict):
                    print(f"    Ключи moderator_evaluation: {list(mod_eval.keys())}")
        else:
            print(f"Тип данных: {type(sample_data)}")
            print(f"Содержимое: {str(sample_data)[:200]}")
    
    # 3. Ищем конкретные пропущенные записи
    print("\n🔎 ПОИСК КОНКРЕТНЫХ ЗАПИСЕЙ:")
    
    all_partial_results = []
    for pf in partial_files:
        try:
            with open(pf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_partial_results.extend(data)
                else:
                    all_partial_results.append(data)
        except Exception as e:
            print(f"Ошибка чтения {pf}: {e}")
    
    print(f"Всего записей в partial: {len(all_partial_results)}")
    
    # Проверяем наличие каждой пропущенной записи
    found_count = 0
    for na_key in na_keys:
        found = False
        seg_id, engine = na_key.split('_')
        
        for rec in all_partial_results:
            rec_seg = str(rec.get('segment_id', ''))
            rec_eng = rec.get('translation_engine', '')
            
            if rec_seg == seg_id and rec_eng == engine:
                found = True
                found_count += 1
                print(f"\n✅ НАЙДЕНА: {na_key}")
                
                # Показываем, что в записи
                mod_eval = rec.get('moderator_evaluation', {})
                if isinstance(mod_eval, dict):
                    print(f"  moderator_evaluation: {mod_eval}")
                    if 'final_score' in mod_eval:
                        print(f"  ✅ final_score = {mod_eval['final_score']}")
                    else:
                        print(f"  ❌ нет final_score в moderator_evaluation")
                else:
                    print(f"  ❌ moderator_evaluation не словарь: {type(mod_eval)}")
                break
        
        if not found:
            print(f"❌ НЕ НАЙДЕНА: {na_key}")
    
    print(f"\n📊 Итого найдено: {found_count} из {len(na_keys)}")
    
    # 4. Статистика по partial файлам
    print("\n📈 СТАТИСТИКА ПО PARTIAL ФАЙЛАМ:")
    themes = Counter()
    engines = Counter()
    
    for rec in all_partial_results:
        themes[rec.get('theme', 'unknown')] += 1
        engines[rec.get('translation_engine', 'unknown')] += 1
    
    print(f"Тематики: {dict(themes)}")
    print(f"Движки: {dict(engines)}")

if __name__ == "__main__":
    debug_na()