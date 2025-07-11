#!/usr/bin/env python3
"""
Migration script for RumiAI v1 to v2.

Handles data migration and compatibility.
AUTOMATED - NO HUMAN INTERVENTION REQUIRED.
"""
import json
import shutil
from pathlib import Path
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rumiai_v2.core.models import UnifiedAnalysis, Timestamp, Timeline, TimelineEvent
from rumiai_v2.utils import Logger

logger = Logger.setup('migration', level='INFO')


class RumiAIMigrator:
    """Migrate RumiAI v1 data to v2 format."""
    
    def __init__(self, backup: bool = True):
        """
        Initialize migrator.
        
        Args:
            backup: Whether to backup files before migration
        """
        self.backup = backup
        self.stats = {
            'files_found': 0,
            'files_migrated': 0,
            'files_failed': 0,
            'backups_created': 0
        }
    
    def migrate_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate all v1 data to v2 format.
        
        Args:
            dry_run: If True, only simulate migration
            
        Returns:
            Migration statistics
        """
        logger.info("Starting RumiAI v1 to v2 migration")
        
        # Find all v1 data directories
        v1_dirs = [
            Path("unified_analysis"),
            Path("temporal_markers"),
            Path("insights")
        ]
        
        for v1_dir in v1_dirs:
            if v1_dir.exists():
                logger.info(f"Found v1 directory: {v1_dir}")
                self._migrate_directory(v1_dir, dry_run)
        
        # Migrate standalone files
        self._migrate_standalone_files(dry_run)
        
        logger.info(f"Migration complete: {self.stats}")
        return self.stats
    
    def _migrate_directory(self, v1_dir: Path, dry_run: bool) -> None:
        """Migrate a v1 directory."""
        if v1_dir.name == "unified_analysis":
            self._migrate_unified_analyses(v1_dir, dry_run)
        elif v1_dir.name == "temporal_markers":
            logger.info("Temporal markers will be regenerated in v2")
        elif v1_dir.name == "insights":
            self._migrate_insights(v1_dir, dry_run)
    
    def _migrate_unified_analyses(self, v1_dir: Path, dry_run: bool) -> None:
        """Migrate unified analysis files."""
        v2_dir = Path("rumiai_v2_data/unified")
        
        for json_file in v1_dir.glob("*.json"):
            self.stats['files_found'] += 1
            
            try:
                logger.info(f"Migrating unified analysis: {json_file}")
                
                # Load v1 data
                with open(json_file, 'r') as f:
                    v1_data = json.load(f)
                
                # Convert to v2 format
                v2_data = self._convert_unified_analysis(v1_data)
                
                if not dry_run:
                    # Backup if requested
                    if self.backup:
                        backup_path = json_file.with_suffix('.json.v1_backup')
                        shutil.copy2(json_file, backup_path)
                        self.stats['backups_created'] += 1
                    
                    # Save v2 format
                    v2_dir.mkdir(parents=True, exist_ok=True)
                    v2_path = v2_dir / json_file.name
                    
                    # Use UnifiedAnalysis model to ensure validity
                    analysis = UnifiedAnalysis.from_dict(v2_data)
                    analysis.save_to_file(str(v2_path))
                    
                logger.info(f"✅ Migrated: {json_file.name}")
                self.stats['files_migrated'] += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate {json_file}: {e}")
                self.stats['files_failed'] += 1
    
    def _convert_unified_analysis(self, v1_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v1 unified analysis to v2 format."""
        # Start with v1 data
        v2_data = v1_data.copy()
        
        # Ensure required fields
        v2_data.setdefault('version', '2.0.0')
        v2_data.setdefault('created_at', datetime.utcnow().isoformat() + 'Z')
        
        # Convert timeline if present
        if 'timeline' in v2_data and isinstance(v2_data['timeline'], dict):
            v2_data['timeline'] = self._convert_timeline(v2_data['timeline'])
        
        # Convert ML results
        if 'ml_results' in v2_data:
            v2_data['ml_results'] = self._convert_ml_results(v2_data['ml_results'])
        
        # Ensure video_metadata
        if 'video_metadata' not in v2_data and 'metadata' in v2_data:
            v2_data['video_metadata'] = v2_data.pop('metadata')
        
        return v2_data
    
    def _convert_timeline(self, v1_timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v1 timeline to v2 format."""
        v2_timeline = {
            'duration': v1_timeline.get('duration', 0.0),
            'events': []
        }
        
        # Convert events
        for event in v1_timeline.get('events', []):
            v2_event = self._convert_timeline_event(event)
            if v2_event:
                v2_timeline['events'].append(v2_event)
        
        return v2_timeline
    
    def _convert_timeline_event(self, v1_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert v1 timeline event to v2 format."""
        try:
            # Parse timestamp
            ts_value = v1_event.get('timestamp', v1_event.get('time', 0))
            timestamp = Timestamp.from_value(ts_value)
            
            if timestamp is None:
                logger.warning(f"Skipping event with invalid timestamp: {ts_value}")
                return None
            
            return {
                'timestamp': timestamp.to_dict(),
                'event_type': v1_event.get('type', v1_event.get('event_type', 'unknown')),
                'description': v1_event.get('description', ''),
                'source': v1_event.get('source', 'v1_migration'),
                'confidence': float(v1_event.get('confidence', 0.8)),
                'metadata': v1_event.get('metadata', {})
            }
        except Exception as e:
            logger.warning(f"Failed to convert event: {e}")
            return None
    
    def _convert_ml_results(self, v1_ml: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v1 ML results to v2 format."""
        v2_ml = {}
        
        for model_name, result in v1_ml.items():
            if isinstance(result, dict):
                v2_ml[model_name] = {
                    'model_name': model_name,
                    'success': result.get('success', True),
                    'data': result.get('data', result),
                    'processing_time': float(result.get('processing_time', 0.0)),
                    'metadata': result.get('metadata', {})
                }
            else:
                # Handle non-dict results
                v2_ml[model_name] = {
                    'model_name': model_name,
                    'success': True,
                    'data': result,
                    'processing_time': 0.0,
                    'metadata': {}
                }
        
        return v2_ml
    
    def _migrate_insights(self, v1_dir: Path, dry_run: bool) -> None:
        """Migrate insights directory."""
        v2_dir = Path("rumiai_v2_data/insights")
        
        if not dry_run and not v2_dir.exists():
            logger.info(f"Copying insights directory to v2 location")
            shutil.copytree(v1_dir, v2_dir)
            self.stats['files_migrated'] += 1
    
    def _migrate_standalone_files(self, dry_run: bool) -> None:
        """Migrate standalone configuration files."""
        config_files = [
            ("config.json", "rumiai_v2_data/config/settings.json"),
            (".env", ".env"),
            ("CLAUDE.md", "CLAUDE.md")
        ]
        
        for src_name, dst_name in config_files:
            src = Path(src_name)
            dst = Path(dst_name)
            
            if src.exists():
                self.stats['files_found'] += 1
                
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    if self.backup and dst.exists():
                        backup = dst.with_suffix(dst.suffix + '.v1_backup')
                        shutil.copy2(dst, backup)
                        self.stats['backups_created'] += 1
                    
                    shutil.copy2(src, dst)
                    logger.info(f"Copied {src} to {dst}")
                    self.stats['files_migrated'] += 1


def main():
    """Run migration."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate RumiAI v1 to v2')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Simulate migration without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backups')
    
    args = parser.parse_args()
    
    print("🔄 RumiAI v1 to v2 Migration Tool")
    print("=" * 40)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
    
    migrator = RumiAIMigrator(backup=not args.no_backup)
    stats = migrator.migrate_all(dry_run=args.dry_run)
    
    print("\n📊 Migration Summary:")
    print(f"Files found: {stats['files_found']}")
    print(f"Files migrated: {stats['files_migrated']}")
    print(f"Files failed: {stats['files_failed']}")
    print(f"Backups created: {stats['backups_created']}")
    
    if stats['files_failed'] > 0:
        print("\n❌ Some files failed to migrate. Check logs for details.")
        sys.exit(1)
    else:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()