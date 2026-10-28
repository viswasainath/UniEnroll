#!/usr/bin/env python3
"""
UniEnroll FFCS Seed Script
Executes full graph seeding for VIT Chennai FFCS simulation.
Usage:
    python3 seed.py
"""
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.database import Neo4jManager
from backend.services.seed_service import SeedService

def main():
    print("🚀 Starting UniEnroll FFCS Database Seeding...")
    try:
        driver = Neo4jManager.get_driver()
        with driver.session() as session:
            result = SeedService.reset_and_seed(session)
            print("✅ Seeding completed:", result["message"])
            
            # Print summary
            health = Neo4jManager.check_connection()
            print("\n📊 Database Graph Status:")
            for label, count in health["node_counts"].items():
                print(f"   • {label}: {count} nodes")
            print(f"   • Total Relationships: {health['total_relationships']}")
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        sys.exit(1)
    finally:
        Neo4jManager.close()

if __name__ == "__main__":
    main()
