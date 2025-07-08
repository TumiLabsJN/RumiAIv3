#!/usr/bin/env python3
"""
Temporal Marker Rollout Controller
Manages gradual rollout of temporal markers with automated health checks
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from python.temporal_monitoring import check_rollout_health, get_monitor
from python.claude_temporal_integration import ClaudeTemporalIntegration


class TemporalRolloutController:
    """Controls temporal marker rollout with safety checks"""
    
    def __init__(self, config_path: str = "config/temporal_markers.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.rollout_history = self._load_rollout_history()
        
    def _load_config(self) -> dict:
        """Load current configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "enable_temporal_markers": False,
            "rollout_percentage": 0.0,
            "format_options": {}
        }
    
    def _save_config(self):
        """Save configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✅ Configuration saved to {self.config_path}")
    
    def _load_rollout_history(self) -> list:
        """Load rollout history"""
        history_path = self.config_path.parent / "rollout_history.json"
        if history_path.exists():
            with open(history_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_rollout_history(self):
        """Save rollout history"""
        history_path = self.config_path.parent / "rollout_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.rollout_history, f, indent=2)
    
    def get_current_status(self) -> dict:
        """Get current rollout status"""
        return {
            "enabled": self.config.get("enable_temporal_markers", False),
            "percentage": self.config.get("rollout_percentage", 0.0),
            "last_change": self.rollout_history[-1]["timestamp"] if self.rollout_history else None,
            "total_changes": len(self.rollout_history)
        }
    
    def can_increase_rollout(self) -> tuple[bool, list[str]]:
        """Check if rollout can be safely increased"""
        health = check_rollout_health()
        reasons = []
        
        if not health['healthy']:
            reasons.extend(health['recommendations'])
            return False, reasons
        
        # Check minimum time since last change (e.g., 24 hours)
        if self.rollout_history:
            last_change = datetime.fromisoformat(self.rollout_history[-1]["timestamp"])
            hours_since = (datetime.now() - last_change).total_seconds() / 3600
            if hours_since < 24:
                reasons.append(f"Only {hours_since:.1f} hours since last change (min 24h)")
                return False, reasons
        
        # Check if already at 100%
        if self.config.get("rollout_percentage", 0) >= 100:
            reasons.append("Already at 100% rollout")
            return False, reasons
        
        return True, []
    
    def update_rollout(self, new_percentage: float, force: bool = False) -> bool:
        """Update rollout percentage with safety checks"""
        current_percentage = self.config.get("rollout_percentage", 0.0)
        
        # Validate percentage
        if new_percentage < 0 or new_percentage > 100:
            print("❌ Percentage must be between 0 and 100")
            return False
        
        # Check if decreasing (always allowed)
        if new_percentage < current_percentage:
            self._apply_rollout_change(new_percentage, "Manual decrease")
            return True
        
        # Check if increasing
        if new_percentage > current_percentage:
            can_increase, reasons = self.can_increase_rollout()
            
            if not can_increase and not force:
                print("❌ Cannot increase rollout:")
                for reason in reasons:
                    print(f"   - {reason}")
                print("\nUse --force to override safety checks")
                return False
            
            if force and not can_increase:
                print("⚠️  Forcing rollout increase despite warnings:")
                for reason in reasons:
                    print(f"   - {reason}")
            
            self._apply_rollout_change(new_percentage, "Manual increase" + (" (forced)" if force else ""))
            return True
        
        print("ℹ️  No change needed")
        return True
    
    def _apply_rollout_change(self, new_percentage: float, reason: str):
        """Apply rollout percentage change"""
        old_percentage = self.config.get("rollout_percentage", 0.0)
        
        # Update config
        self.config["rollout_percentage"] = new_percentage
        if new_percentage > 0:
            self.config["enable_temporal_markers"] = True
        
        # Save config
        self._save_config()
        
        # Record in history
        self.rollout_history.append({
            "timestamp": datetime.now().isoformat(),
            "old_percentage": old_percentage,
            "new_percentage": new_percentage,
            "reason": reason,
            "health_status": check_rollout_health()
        })
        self._save_rollout_history()
        
        print(f"✅ Rollout updated: {old_percentage}% → {new_percentage}%")
        
        # Update environment variable
        os.environ['TEMPORAL_ROLLOUT_PERCENTAGE'] = str(new_percentage)
        print(f"✅ Environment variable updated")
    
    def enable_temporal_markers(self):
        """Enable temporal markers (0% rollout)"""
        self.config["enable_temporal_markers"] = True
        self.config["rollout_percentage"] = 0.0
        self._save_config()
        print("✅ Temporal markers enabled (0% rollout)")
    
    def disable_temporal_markers(self):
        """Disable temporal markers completely"""
        self.config["enable_temporal_markers"] = False
        self._save_config()
        os.environ['ENABLE_TEMPORAL_MARKERS'] = 'false'
        print("✅ Temporal markers disabled")
    
    def apply_phased_rollout(self, phase: int):
        """Apply pre-defined phased rollout"""
        phases = {
            1: {"percentage": 10, "description": "Initial testing"},
            2: {"percentage": 50, "description": "Expanded testing"},
            3: {"percentage": 100, "description": "Full rollout"}
        }
        
        if phase not in phases:
            print(f"❌ Invalid phase. Choose from: {list(phases.keys())}")
            return
        
        phase_config = phases[phase]
        print(f"\n📊 Applying Phase {phase}: {phase_config['description']}")
        print(f"   Target: {phase_config['percentage']}% rollout")
        
        self.update_rollout(phase_config['percentage'])
    
    def show_rollout_history(self):
        """Display rollout history"""
        print("\n📜 ROLLOUT HISTORY")
        print("="*80)
        
        if not self.rollout_history:
            print("No rollout changes recorded")
            return
        
        for i, change in enumerate(self.rollout_history):
            print(f"\n{i+1}. {change['timestamp']}")
            print(f"   Change: {change['old_percentage']}% → {change['new_percentage']}%")
            print(f"   Reason: {change['reason']}")
            if 'health_status' in change:
                health = change['health_status']
                print(f"   Health: {'✅ Healthy' if health.get('healthy', False) else '⚠️  Issues'}")


def main():
    controller = TemporalRolloutController()
    
    if len(sys.argv) < 2:
        # Show current status
        status = controller.get_current_status()
        print("\n📊 TEMPORAL MARKER ROLLOUT STATUS")
        print("="*50)
        print(f"Enabled: {'✅' if status['enabled'] else '❌'}")
        print(f"Current Rollout: {status['percentage']}%")
        print(f"Last Changed: {status['last_change'] or 'Never'}")
        print(f"Total Changes: {status['total_changes']}")
        
        print("\nUsage:")
        print("  python temporal_rollout_controller.py <command> [options]")
        print("\nCommands:")
        print("  enable              Enable temporal markers (0% rollout)")
        print("  disable             Disable temporal markers completely")
        print("  set <percentage>    Set rollout percentage (0-100)")
        print("  phase <1|2|3>       Apply phased rollout")
        print("  history             Show rollout history")
        print("  status              Show current status (default)")
        print("\nOptions:")
        print("  --force            Override safety checks")
        return
    
    command = sys.argv[1]
    
    if command == "enable":
        controller.enable_temporal_markers()
    
    elif command == "disable":
        controller.disable_temporal_markers()
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("❌ Please specify percentage: set <percentage>")
            return
        try:
            percentage = float(sys.argv[2])
            force = "--force" in sys.argv
            controller.update_rollout(percentage, force=force)
        except ValueError:
            print("❌ Invalid percentage. Must be a number between 0 and 100")
    
    elif command == "phase":
        if len(sys.argv) < 3:
            print("❌ Please specify phase: phase <1|2|3>")
            return
        try:
            phase = int(sys.argv[2])
            controller.apply_phased_rollout(phase)
        except ValueError:
            print("❌ Invalid phase. Must be 1, 2, or 3")
    
    elif command == "history":
        controller.show_rollout_history()
    
    elif command == "status":
        # Already shown above
        pass
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()