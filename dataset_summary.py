#!/usr/bin/env python3
"""
Training Dataset Summary & Statistics Report
Analyzes the generated fraud detection training dataset
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

def analyze_json_dataset(json_file):
    """Analyze JSON dataset structure"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("  TRAINING DATASET SUMMARY & STATISTICS")
    print("="*80 + "\n")
    
    print(f"📊 Dataset Generated: {json_file}")
    print(f"   File Size: {json_file.stat().st_size:,} bytes")
    print(f"   Format: JSON (structured) + CSV (analytics)\n")
    
    # Scenario statistics
    print("📋 SCENARIOS TESTED:")
    print("-" * 80)
    
    scenario_stats = defaultdict(lambda: {
        'turns': 0,
        'scams_detected': 0,
        'avg_confidence': 0,
        'confidence_scores': []
    })
    
    total_turns = 0
    total_scams = 0
    
    for scenario in data:
        scenario_name = scenario['scenario']
        scenario_type = scenario['type']
        channel = scenario['channel']
        num_turns = len(scenario['turns'])
        
        scams_in_scenario = sum(1 for turn in scenario['turns'] if turn['scam_detected'])
        confidences = [turn['confidence'] for turn in scenario['turns']]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        print(f"\n  ✓ {scenario_type}")
        print(f"    └─ ID: {scenario_name}")
        print(f"    └─ Channel: {channel}")
        print(f"    └─ Turns: {num_turns}")
        print(f"    └─ Scams Detected: {scams_in_scenario}/{num_turns}")
        print(f"    └─ Avg Confidence: {avg_conf:.3f}")
        print(f"    └─ Sample Conversation:")
        print(f"       Turn 1 (Early): \"{scenario['turns'][0]['victim_reply']}\"")
        mid = len(scenario['turns']) // 2
        print(f"       Turn {mid} (Middle): \"{scenario['turns'][mid-1]['victim_reply']}\"")
        print(f"       Turn {num_turns} (Late): \"{scenario['turns'][-1]['victim_reply']}\"")
        
        total_turns += num_turns
        total_scams += scams_in_scenario
        scenario_stats[scenario_name]['turns'] = num_turns
        scenario_stats[scenario_name]['scams_detected'] = scams_in_scenario
        scenario_stats[scenario_name]['confidence_scores'] = confidences
    
    # Overall statistics
    print("\n" + "="*80)
    print("📈 OVERALL STATISTICS:")
    print("-" * 80)
    
    all_confidences = []
    for stats in scenario_stats.values():
        all_confidences.extend(stats['confidence_scores'])
    
    avg_overall_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    max_confidence = max(all_confidences) if all_confidences else 0
    min_confidence = min(all_confidences) if all_confidences else 0
    
    print(f"\nTotal Scenarios: {len(data)}")
    print(f"Total Conversation Turns: {total_turns}")
    print(f"Scams Detected: {total_scams}/{total_turns}")
    print(f"Detection Rate: {(total_scams/total_turns*100):.1f}%")
    print(f"\nConfidence Scores:")
    print(f"  • Average: {avg_overall_confidence:.3f}")
    print(f"  • Maximum: {max_confidence:.3f}")
    print(f"  • Minimum: {min_confidence:.3f}")
    
    # Conversation progression analysis
    print("\n" + "="*80)
    print("🔄 CONVERSATION PROGRESSION ANALYSIS:")
    print("-" * 80)
    
    print("\n  Turn 1 (Early Stage - Victim Skepticism):")
    for scenario in data:
        victim_msg = scenario['turns'][0]['victim_reply']
        print(f"    • {victim_msg}")
    
    print("\n  Middle Turns (Victim Engagement):")
    for scenario in data:
        mid = len(scenario['turns']) // 2
        if mid > 0:
            victim_msg = scenario['turns'][mid-1]['victim_reply']
            print(f"    • {victim_msg}")
    
    print("\n  Final Turns (Victim Compliance):")
    for scenario in data:
        victim_msg = scenario['turns'][-1]['victim_reply']
        print(f"    • {victim_msg}")
    
    # Dataset use cases
    print("\n" + "="*80)
    print("🎯 TRAINING DATASET USE CASES:")
    print("-" * 80)
    print("""
  1. Fraud Detection Model Training
     • Multi-turn scam conversation patterns
     • Victim engagement progression detection
     • Confidence scoring calibration
  
  2. Scammer Tactic Analysis
     • KYC expiry threats
     • Reward/cashback lures
     • Urgency and pressure tactics
     • Authority impersonation
  
  3. Conversation Flow Understanding
     • Early-stage skepticism patterns
     • Engagement and trust-building phases
     • Compliance requests sequence
     • Victim response consistency
  
  4. Model Evaluation
     • {0} labeled scam turns
     • {1} unlabeled turns (multi-class)
     • {2} total conversations
     • Real victim response patterns
    """.format(total_scams, total_turns - total_scams, len(data)))
    
    # Files created
    print("="*80)
    print("📁 OUTPUT FILES:")
    print("-" * 80)
    csv_file = Path('training_dataset.csv')
    json_file = Path('training_dataset.json')
    print(f"\n  1. training_dataset.json ({json_file.stat().st_size:,} bytes)")
    print(f"     ├─ Structured format for ML pipelines")
    print(f"     ├─ Complete conversation objects")
    print(f"     └─ Per-turn scam detection flags")
    print(f"\n  2. training_dataset.csv ({csv_file.stat().st_size:,} bytes)")
    print(f"     ├─ Analytics-friendly format")
    print(f"     ├─ One row per conversation turn")
    print(f"     └─ Easy import to pandas/sklearn")
    
    print("\n" + "="*80)
    print("✅ Dataset ready for fraud detection model training!")
    print("="*80 + "\n")

if __name__ == "__main__":
    json_file = Path('training_dataset.json')
    if json_file.exists():
        analyze_json_dataset(json_file)
    else:
        print("training_dataset.json not found!")
