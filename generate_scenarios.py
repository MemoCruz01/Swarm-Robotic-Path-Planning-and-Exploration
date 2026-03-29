"""
Generate multiple animations with different Phase 4 configurations.
Creates several GIFs showcasing different scenarios and complexity levels.
"""

import subprocess
import numpy as np
from datetime import datetime
import shutil
import os

# Configuration scenarios to test
SCENARIOS = [
    {
        'name': 'Baseline - No Terrain Zones',
        'mods': {
            'TERRAIN_ENABLED': 'False',
            'DYNAMIC_OBSTACLES': 'True',
            'DYNAMIC_OBSTACLE_COUNT': '2',
        },
        'description': 'Phase 4 with only dynamic obstacles, no terrain'
    },
    {
        'name': 'High Terrain Load',
        'mods': {
            'TERRAIN_ENABLED': 'True',
            'TERRAIN_FRICTION_ZONES': 'True',
            'DYNAMIC_OBSTACLES': 'False',
        },
        'description': 'Phase 4 with terrain zones only, no obstacles'
    },
    {
        'name': 'Heavy Obstacles',
        'mods': {
            'TERRAIN_ENABLED': 'False',
            'DYNAMIC_OBSTACLES': 'True',
            'DYNAMIC_OBSTACLE_COUNT': '5',
            'MAX_CONCURRENT_DYNAMIC_OBSTACLES': '8',
        },
        'description': 'Phase 4 with 5 dynamic obstacles, more challenging'
    },
    {
        'name': 'Full Complexity',
        'mods': {
            'TERRAIN_ENABLED': 'True',
            'TERRAIN_FRICTION_ZONES': 'True',
            'TERRAIN_SLIPPY_ZONES': 'True',
            'DYNAMIC_OBSTACLES': 'True',
            'DYNAMIC_OBSTACLE_COUNT': '3',
        },
        'description': 'Phase 4 with terrain (friction + slippy) + 3 obstacles'
    },
    {
        'name': 'Few Robots',
        'mods': {
            'NUM_ROBOTS': '5',
            'TERRAIN_ENABLED': 'True',
            'DYNAMIC_OBSTACLES': 'True',
            'DYNAMIC_OBSTACLE_COUNT': '2',
        },
        'description': 'Only 5 robots with terrain and obstacles'
    },
    {
        'name': 'Many Robots',
        'mods': {
            'NUM_ROBOTS': '25',
            'TERRAIN_ENABLED': 'True',
            'DYNAMIC_OBSTACLES': 'True',
            'DYNAMIC_OBSTACLE_COUNT': '3',
        },
        'description': '25 robots navigating complex environment'
    },
]

def backup_config():
    """Backup original config files."""
    print("📦 Backing up original configuration...")
    shutil.copy(
        'config/settings.py',
        'config/settings.py.backup'
    )
    shutil.copy(
        'config/realism_settings.py',
        'config/realism_settings.py.backup'
    )
    print("✓ Backup created")

def restore_config():
    """Restore original config files."""
    print("🔄 Restoring original configuration...")
    if os.path.exists('config/settings.py.backup'):
        shutil.copy(
            'config/settings.py.backup',
            'config/settings.py'
        )
    if os.path.exists('config/realism_settings.py.backup'):
        shutil.copy(
            'config/realism_settings.py.backup',
            'config/realism_settings.py'
        )
    print("✓ Configuration restored")

def modify_config(modifications):
    """Modify realism_settings.py with scenario-specific values."""
    print(f"  Modifying configuration...")
    
    with open('config/realism_settings.py', 'r') as f:
        content = f.read()
    
    for key, value in modifications.items():
        # Find and replace the parameter
        pattern = f"{key} = "
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(pattern):
                # Preserve comments
                if '#' in line:
                    comment = line[line.index('#'):]
                    lines[i] = f"{key} = {value}  # {comment}"
                else:
                    lines[i] = f"{key} = {value}"
                break
        content = '\n'.join(lines)
    
    with open('config/realism_settings.py', 'w') as f:
        f.write(content)
    print(f"    ✓ Applied {len(modifications)} configuration changes")

def run_animation(scenario_name):
    """Run save_animation.py to generate a GIF."""
    print(f"\n  Running animation generation...")
    result = subprocess.run(
        ['.venv\\Scripts\\python.exe', 'save_animation.py'],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if result.returncode == 0:
        print(f"  ✓ Animation generated successfully")
    else:
        print(f"  ✗ Animation generation had issues:")
        print(result.stdout[-500:] if result.stdout else "No output")
    
    return result.returncode == 0

def generate_all_scenarios():
    """Generate animations for all scenarios."""
    print("=" * 70)
    print("GENERATING MULTIPLE PHASE 4 TEST SCENARIOS")
    print("=" * 70)
    print()
    
    # Backup original configs
    backup_config()
    
    successful = []
    failed = []
    
    try:
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"\n[{i}/{len(SCENARIOS)}] {scenario['name']}")
            print(f"     {scenario['description']}")
            print(f"     {'-' * 60}")
            
            try:
                # Restore clean config first
                restore_config()
                
                # Apply modifications
                modify_config(scenario['mods'])
                
                # Run animation
                success = run_animation(scenario['name'])
                
                if success:
                    successful.append(scenario['name'])
                    print(f"     ✓ {scenario['name']} - COMPLETE")
                else:
                    failed.append(scenario['name'])
                    print(f"     ✗ {scenario['name']} - FAILED")
                    
            except Exception as e:
                failed.append(scenario['name'])
                print(f"     ✗ Error: {str(e)}")
    
    finally:
        # Restore original config
        restore_config()
    
    # Print summary
    print("\n" + "=" * 70)
    print("ANIMATION GENERATION SUMMARY")
    print("=" * 70)
    print(f"\n✓ Successful: {len(successful)}/{len(SCENARIOS)}")
    for name in successful:
        print(f"  ✓ {name}")
    
    if failed:
        print(f"\n✗ Failed: {len(failed)}/{len(SCENARIOS)}")
        for name in failed:
            print(f"  ✗ {name}")
    
    print("\n📁 All animations saved to: outputs/animations/")
    print("\n🎯 You can now compare different scenarios by opening the GIFs:")
    print("   - Baseline shows optimal case")
    print("   - High Terrain Load shows friction effects")
    print("   - Heavy Obstacles shows avoidance complexity")
    print("   - Full Complexity shows worst case")
    print("   - Few Robots shows small swarm behavior")
    print("   - Many Robots shows scalability")

if __name__ == "__main__":
    generate_all_scenarios()
