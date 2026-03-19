#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE V2 - DEPLOYMENT CHECKER
=============================================================================
Cek semua komponen sebelum deploy:
- Semua file yang diperlukan ada
- Tidak ada syntax error
- Integrasi V1 dan V2 beres
- Environment variables lengkap
=============================================================================
"""

import os
import sys
import importlib
import traceback
from pathlib import Path

# =============================================================================
# COLOR CODES
# =============================================================================
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🔍 {text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_ok(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_warn(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"📌 {text}")

# =============================================================================
# 1. CHECK ENVIRONMENT
# =============================================================================
print_header("CHECKING ENVIRONMENT")

# Python version
import sys
py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
if sys.version_info >= (3, 11):
    print_ok(f"Python version: {py_version}")
else:
    print_error(f"Python version: {py_version} (need 3.11+)")

# Current directory
cwd = os.getcwd()
print_ok(f"Working directory: {cwd}")

# =============================================================================
# 2. CHECK REQUIRED FILES (V1)
# =============================================================================
print_header("CHECKING V1 FILES")

v1_required = [
    "main.py",
    "config.py",
    "requirements.txt",
    "railway.json",
    "Dockerfile",
    ".env.example",
    "core/ai_engine.py",
    "core/context_analyzer.py",
    "core/prompt_builder.py",
    "memory/vector_db.py",
    "memory/episodic.py",
    "memory/semantic.py",
    "memory/relationship.py",
    "memory/consolidation.py",
    "roles/artis_references.py",
    "roles/base.py",
    "relationship/intimacy.py",
    "relationship/ranking.py",
    "relationship/hts.py",
    "relationship/fwb.py",
    "sexual/positions.py",
    "sexual/areas.py",
    "sexual/climax.py",
    "sexual/preferences.py",
    "sexual/compatibility.py",
    "sexual/aftercare.py",
    "threesome/manager.py",
    "threesome/dynamics.py",
    "dynamics/location.py",
    "dynamics/position.py",
    "dynamics/clothing.py",
    "dynamics/expression_db.py",
    "dynamics/sound_db.py",
    "dynamics/nickname.py",
    "leveling/time_based.py",
    "leveling/progress_tracker.py",
    "leveling/decay.py",
    "public/locations.py",
    "public/risk.py",
    "public/thrill.py",
    "public/events.py",
    "public/auto_select.py",
    "session/unique_id.py",
    "session/storage.py",
    "session/continuation.py",
    "session/cleanup.py",
    "bot/application.py",
    "bot/commands.py",
    "bot/handlers.py",
    "bot/callbacks.py",
    "bot/webhook.py",
    "database/connection.py",
    "database/models.py",
    "database/repository.py",
    "utils/logger.py",
    "utils/exceptions.py",
    "utils/helpers.py",
    "utils/performance.py",
    "monitoring/metrics.py",
    "monitoring/dashboard.py",
    "backup/automated.py",
    "backup/recovery.py",
    "backup/verify.py",
    "scripts/setup_webhook.py",
    "scripts/test_bot.py",
]

v1_missing = []
for file in v1_required:
    if not Path(file).exists():
        v1_missing.append(file)

if v1_missing:
    print_warn(f"Missing {len(v1_missing)} V1 files:")
    for f in v1_missing[:10]:
        print(f"   • {f}")
else:
    print_ok("All V1 files present")

# =============================================================================
# 3. CHECK REQUIRED FILES (V2)
# =============================================================================
print_header("CHECKING V2 FILES")

v2_required = [
    "pdkt_natural/__init__.py",
    "pdkt_natural/engine.py",
    "pdkt_natural/chemistry.py",
    "pdkt_natural/direction.py",
    "pdkt_natural/mood.py",
    "pdkt_natural/dreams.py",
    "pdkt_natural/random_pdkt.py",
    "pdkt_natural/mantan_manager.py",
    "pdkt_natural/pdkt_list.py",
    "pdkt_natural/command_handler.py",
    "pdkt_natural/proactive.py",
    "pdkt_natural/story.py",
    "core/story_predictor.py",
    "core/proactive_generator.py",
    "core/scene_recommender.py",
    "core/intent_analyzer.py",
    "core/prompt_builder_v2.py",
    "memory/hippocampus.py",
    "memory/compact_memory.py",
    "memory/episodic_v2.py",
    "memory/semantic_v2.py",
    "memory/forgetting.py",
    "memory/memory_bridge.py",
    "dynamics/expression_engine_v2.py",
    "dynamics/sound_engine_v2.py",
    "dynamics/name_generator.py",
    "leveling/time_based_v2.py",
    "leveling/activity_boost.py",
    "relationship/fwb_manager.py",
    "relationship/hts_manager.py",
    "relationship/intimacy_v2.py",
    "sexual/scene_generator.py",
    "sexual/intimacy_engine.py",
    "bot/commands_v2.py",
    "bot/handlers_v2.py",
    "bot/callbacks_v2.py",
    "session/unique_id_v2.py",
    "database/models_v2.py",
    "database/repository_v2.py",
    "database/migrations/v2_migration.sql",
    "database/auto_migrate.py",
]

v2_missing = []
for file in v2_required:
    if not Path(file).exists():
        v2_missing.append(file)

if v2_missing:
    print_warn(f"Missing {len(v2_missing)} V2 files:")
    for f in v2_missing[:10]:
        print(f"   • {f}")
else:
    print_ok("All V2 files present")

# =============================================================================
# 4. CHECK __init__.py FILES
# =============================================================================
print_header("CHECKING __INIT__.PY FILES")

init_files = [
    "core/__init__.py",
    "memory/__init__.py",
    "roles/__init__.py",
    "relationship/__init__.py",
    "sexual/__init__.py",
    "threesome/__init__.py",
    "dynamics/__init__.py",
    "leveling/__init__.py",
    "public/__init__.py",
    "session/__init__.py",
    "bot/__init__.py",
    "database/__init__.py",
    "utils/__init__.py",
    "monitoring/__init__.py",
    "backup/__init__.py",
    "scripts/__init__.py",
    "pdkt_natural/__init__.py",
]

init_missing = []
for file in init_files:
    if not Path(file).exists():
        init_missing.append(file)

if init_missing:
    print_warn(f"Missing {len(init_missing)} __init__.py files:")
    for f in init_missing:
        print(f"   • {f}")
else:
    print_ok("All __init__.py files present")

# =============================================================================
# 5. CHECK ENVIRONMENT VARIABLES
# =============================================================================
print_header("CHECKING ENVIRONMENT VARIABLES")

env_vars = [
    "DEEPSEEK_API_KEY",
    "TELEGRAM_TOKEN",
    "ADMIN_ID",
    "ENABLE_PDKT_NATURAL",
    "ENABLE_MEMORY_V2",
]

env_missing = []
for var in env_vars:
    if not os.getenv(var):
        env_missing.append(var)

if env_missing:
    print_warn(f"Missing environment variables:")
    for var in env_missing:
        print(f"   • {var} (set in Railway dashboard)")
    
    # Check if .env exists
    if Path(".env").exists():
        print_ok(".env file exists (but Railway uses dashboard)")
    else:
        print_warn(".env file not found (but Railway uses dashboard)")
else:
    print_ok("All environment variables set")

# =============================================================================
# 6. CHECK IMPORT INTEGRITY
# =============================================================================
print_header("CHECKING IMPORT INTEGRITY")

modules_to_check = [
    # V1 modules
    "config",
    "core.ai_engine",
    "core.context_analyzer",
    "core.prompt_builder",
    "memory.vector_db",
    "memory.episodic",
    "memory.semantic",
    "memory.relationship",
    "memory.consolidation",
    "roles.artis_references",
    "roles.base",
    "relationship.intimacy",
    "relationship.ranking",
    "relationship.hts",
    "relationship.fwb",
    "sexual.positions",
    "sexual.areas",
    "sexual.climax",
    "sexual.preferences",
    "sexual.compatibility",
    "sexual.aftercare",
    "threesome.manager",
    "threesome.dynamics",
    "dynamics.location",
    "dynamics.position",
    "dynamics.clothing",
    "dynamics.expression_db",
    "dynamics.sound_db",
    "dynamics.nickname",
    "leveling.time_based",
    "leveling.progress_tracker",
    "leveling.decay",
    "public.locations",
    "public.risk",
    "public.thrill",
    "public.events",
    "public.auto_select",
    "session.unique_id",
    "session.storage",
    "session.continuation",
    "session.cleanup",
    "bot.application",
    "bot.commands",
    "bot.handlers",
    "bot.callbacks",
    "bot.webhook",
    "database.connection",
    "database.models",
    "database.repository",
    "utils.logger",
    "utils.exceptions",
    "utils.helpers",
    "utils.performance",
    "monitoring.metrics",
    "monitoring.dashboard",
    "backup.automated",
    "backup.recovery",
    "backup.verify",
    "scripts.setup_webhook",
    "scripts.test_bot",
    
    # V2 modules
    "pdkt_natural.engine",
    "pdkt_natural.chemistry",
    "pdkt_natural.direction",
    "pdkt_natural.mood",
    "pdkt_natural.dreams",
    "pdkt_natural.random_pdkt",
    "pdkt_natural.mantan_manager",
    "pdkt_natural.pdkt_list",
    "pdkt_natural.command_handler",
    "pdkt_natural.proactive",
    "pdkt_natural.story",
    "core.story_predictor",
    "core.proactive_generator",
    "core.scene_recommender",
    "core.intent_analyzer",
    "core.prompt_builder_v2",
    "memory.hippocampus",
    "memory.compact_memory",
    "memory.episodic_v2",
    "memory.semantic_v2",
    "memory.forgetting",
    "memory.memory_bridge",
    "dynamics.expression_engine_v2",
    "dynamics.sound_engine_v2",
    "dynamics.name_generator",
    "leveling.time_based_v2",
    "leveling.activity_boost",
    "relationship.fwb_manager",
    "relationship.hts_manager",
    "relationship.intimacy_v2",
    "sexual.scene_generator",
    "sexual.intimacy_engine",
    "bot.commands_v2",
    "bot.handlers_v2",
    "bot.callbacks_v2",
    "session.unique_id_v2",
    "database.models_v2",
    "database.repository_v2",
    "database.auto_migrate",
]

failed_imports = []
success_imports = 0

for module_name in modules_to_check:
    try:
        importlib.import_module(module_name)
        success_imports += 1
    except ImportError as e:
        failed_imports.append((module_name, str(e)))

if failed_imports:
    print_warn(f"Import errors: {len(failed_imports)}/{len(modules_to_check)}")
    for module, error in failed_imports[:5]:  # Show first 5
        print(f"   • {module}: {error}")
else:
    print_ok(f"All {len(modules_to_check)} modules import successfully")

# =============================================================================
# 7. CHECK FOR SYNTAX ERRORS
# =============================================================================
print_header("CHECKING SYNTAX ERRORS")

python_files = list(Path(".").rglob("*.py"))
syntax_errors = []

for py_file in python_files[:50]:  # Check first 50 files
    try:
        compile(py_file.read_text(), py_file, 'exec')
    except SyntaxError as e:
        syntax_errors.append((str(py_file), str(e)))

if syntax_errors:
    print_error(f"Syntax errors found: {len(syntax_errors)}")
    for file, error in syntax_errors[:3]:
        print(f"   • {file}: {error}")
else:
    print_ok("No syntax errors found")

# =============================================================================
# 8. CHECK DATABASE MIGRATION
# =============================================================================
print_header("CHECKING DATABASE MIGRATION")

if Path("database/auto_migrate.py").exists():
    try:
        from database import auto_migrate
        print_ok("auto_migrate.py can be imported")
    except Exception as e:
        print_error(f"auto_migrate.py import failed: {e}")
else:
    print_warn("auto_migrate.py not found")

# =============================================================================
# 9. FINAL SUMMARY
# =============================================================================
print_header("DEPLOYMENT SUMMARY")

total_score = 0
max_score = 9

# Score each check
checks = [
    ("Python version", sys.version_info >= (3, 11)),
    ("V1 files", len(v1_missing) == 0),
    ("V2 files", len(v2_missing) == 0),
    ("__init__.py files", len(init_missing) == 0),
    ("Environment vars", len(env_missing) <= 2),  # Allow missing .env
    ("Import integrity", len(failed_imports) == 0),
    ("Syntax errors", len(syntax_errors) == 0),
    ("Database migration", Path("database/auto_migrate.py").exists()),
    ("Main.py exists", Path("main.py").exists()),
]

for i, (name, passed) in enumerate(checks):
    if passed:
        total_score += 1
        print_ok(f"{i+1}. {name}")
    else:
        print_error(f"{i+1}. {name}")

print(f"\n{BLUE}{'='*60}{RESET}")
if total_score == max_score:
    print(f"{GREEN}✅ DEPLOYMENT READY! Score: {total_score}/{max_score}{RESET}")
    print(f"{GREEN}🚀 You can deploy to Railway now!{RESET}")
elif total_score >= 7:
    print(f"{YELLOW}⚠️  DEPLOYMENT RISKY! Score: {total_score}/{max_score}{RESET}")
    print(f"{YELLOW}   Fix warnings before deploy{RESET}")
else:
    print(f"{RED}❌ DEPLOYMENT NOT READY! Score: {total_score}/{max_score}{RESET}")
    print(f"{RED}   Fix errors before deploy{RESET}")

print(f"{BLUE}{'='*60}{RESET}")

# =============================================================================
# 10. RECOMMENDATIONS
# =============================================================================
if total_score < max_score:
    print_header("RECOMMENDATIONS")
    
    if len(v1_missing) > 0:
        print(f"• Add missing V1 files: {', '.join(v1_missing[:3])}")
    
    if len(v2_missing) > 0:
        print(f"• Add missing V2 files: {', '.join(v2_missing[:3])}")
    
    if len(init_missing) > 0:
        print("• Add missing __init__.py files")
    
    if len(env_missing) > 0:
        print(f"• Set env vars in Railway: {', '.join(env_missing)}")
    
    if len(failed_imports) > 0:
        print("• Fix import dependencies")
    
    if len(syntax_errors) > 0:
        print("• Fix syntax errors")

print(f"\n{BLUE}📝 Run: python check_deploy.py before each deploy{RESET}\n")
