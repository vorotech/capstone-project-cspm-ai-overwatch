import os
import argparse
import pandas as pd

def process_csv(csv_path: str, model_name: str, file_name: str):
    removed = 0
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if 'model' in df.columns:
            initial_len = len(df)
            df = df[df['model'] != model_name]
            removed = initial_len - len(df)
            df.to_csv(csv_path, index=False)
        else:
            print(f"No 'model' column found in {file_name}")
    return removed

def remove_model_history(model_name: str, scenario: str = None):
    """
    Removes all rows matching the specified model_name from
    metrics_history.csv and findings_history.csv.
    If a scenario is specified, it only removes data for that scenario.
    Otherwise, it checks all scenario folders under output/analysis/.
    """
    analysis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'analysis')
    
    scenarios_to_check = []
    if scenario:
        scenarios_to_check.append(scenario)
    else:
        if os.path.exists(analysis_dir):
            for item in os.listdir(analysis_dir):
                if os.path.isdir(os.path.join(analysis_dir, item)):
                    scenarios_to_check.append(item)
                    
    total_removed_metrics = 0
    total_removed_findings = 0
    
    for s in scenarios_to_check:
        scenario_dir = os.path.join(analysis_dir, s)
        metrics_path = os.path.join(scenario_dir, 'metrics_history.csv')
        findings_path = os.path.join(scenario_dir, 'findings_history.csv')
        
        m_removed = process_csv(metrics_path, model_name, f'{s}/metrics_history.csv')
        f_removed = process_csv(findings_path, model_name, f'{s}/findings_history.csv')
        
        if m_removed > 0:
            print(f"Removed {m_removed} rows from {s}/metrics_history.csv for model '{model_name}'.")
            total_removed_metrics += m_removed
        if f_removed > 0:
            print(f"Removed {f_removed} rows from {s}/findings_history.csv for model '{model_name}'.")
            total_removed_findings += f_removed
            
    scenario_msg = f" in scenario '{scenario}'" if scenario else ""
    if total_removed_metrics == 0 and total_removed_findings == 0:
        print(f"No data found for model '{model_name}'{scenario_msg}. Please ensure the name exactly matches the CSV.")
    else:
        print(f"\n[Success] Purged all history for '{model_name}'{scenario_msg}.")
        print("Don't forget to run 'python pipeline/main.py report' to update your charts!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove a specific model's history from the analysis CSVs.")
    parser.add_argument("--model", required=True, help="Exact name of the model to remove (e.g. 'google/gemini-2.5-flash')")
    parser.add_argument("--scenario", required=False, help="Optional specific scenario to remove for the given model")
    
    args = parser.parse_args()
    remove_model_history(args.model, args.scenario)
