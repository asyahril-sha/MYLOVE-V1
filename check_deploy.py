#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - CHECK DEPLOY
=============================================================================
Script untuk memverifikasi semua import dan konfigurasi sebelum deploy ke Railway
Cek: dependencies, environment variables, import modules, dll
=============================================================================
"""

import os
import sys
import importlib
from pathlib import Path

# Tambahkan path ke root project
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Warna untuk output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    """Print header dengan format"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔍 {text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"   • {text}")


def check_import(module_name, attr=None, silent=False):
    """Cek apakah module bisa diimport"""
    try:
        if attr:
            module = importlib.import_module(module_name)
            getattr(module, attr)
            if not silent:
                print_success(f"from {module_name} import {attr}")
        else:
            importlib.import_module(module_name)
            if not silent:
                print_success(f"import {module_name}")
        return True
    except ImportError as e:
        if not silent:
            print_error(f"{module_name} error: {e}")
        return False
    except AttributeError as e:
        if not silent:
            print_error(f"{module_name} missing {attr}: {e}")
        return False


def check_env_file():
    """Cek file .env ada dan terbaca"""
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        print_success(".env file found")
        
        # Load .env file manually untuk cek isi
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
                api_keys = 0
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if value and value != 'your_telegram_bot_token_here' and value != 'your_deepseek_api_key_here':
                                api_keys += 1
                                print_info(f"{key}=**** (terisi)")
                            else:
                                print_warning(f"{key}= (kosong/default)")
                print_info(f"Total {api_keys} API keys terisi")
        except Exception as e:
            print_error(f"Error reading .env: {e}")
    else:
        print_error(".env file not found")
        return False
    return True


def check_environment_variables():
    """Cek environment variables penting"""
    print_header("ENVIRONMENT VARIABLES")
    
    required_vars = [
        'TELEGRAM_TOKEN',
        'DEEPSEEK_API_KEY',
        'ADMIN_ID'
    ]
    
    optional_vars = [
        'PORT',
        'RAILWAY_PUBLIC_DOMAIN',
        'RAILWAY_STATIC_URL',
        'WEBHOOK_URL',
        'WEBHOOK_PORT',
        'WEBHOOK_PATH',
        'DB_TYPE',
        'DB_PATH',
        'LOG_LEVEL',
        'SESSION_RETENTION_DAYS',
        'SEXUAL_CONTENT_ENABLED',
        'BOT_INITIATIVE_ENABLED',
        'AFTERCARE_ENABLED'
    ]
    
    all_ok = True
    
    # Cek required vars
    for var in required_vars:
        value = os.getenv(var)
        if value and value != 'your_telegram_bot_token_here' and value != 'your_deepseek_api_key_here':
            masked = value[:5] + '...' + value[-5:] if len(value) > 10 else '****'
            print_success(f"{var}: {masked}")
        else:
            print_error(f"{var}: MISSING or DEFAULT")
            all_ok = False
    
    # Cek optional vars
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print_info(f"{var}: {value}")
        else:
            print_info(f"{var}: (not set)")
    
    return all_ok


def check_dependencies():
    """Cek dependencies dari requirements.txt"""
    print_header("DEPENDENCIES")
    
    requirements_file = ROOT_DIR / "requirements.txt"
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    all_ok = True
    for req in requirements:
        # Parse package name (ambil sebelum ==, >=, <=, dll)
        if '==' in req:
            package = req.split('==')[0]
        elif '>=' in req:
            package = req.split('>=')[0]
        elif '<=' in req:
            package = req.split('<=')[0]
        else:
            package = req
        
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{req}")
        except ImportError:
            print_error(f"{req} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_config():
    """Cek config.py bisa diimport"""
    print_header("CONFIGURATION")
    
    try:
        from config import settings
        print_success("config.settings imported")
        
        # Cek atribut penting
        attrs = [
            ('telegram_token', 'str'),
            ('deepseek_api_key', 'str'),
            ('admin_id', 'int'),
            ('database', 'DatabaseSettings'),
            ('ai', 'AISettings'),
            ('webhook', 'WebhookSettings'),
            ('logging', 'LoggingSettings'),
        ]
        
        for attr, type_name in attrs:
            if hasattr(settings, attr):
                print_info(f"settings.{attr} exists")
            else:
                print_error(f"settings.{attr} missing")
        
        # Cek database path
        if hasattr(settings, 'database') and hasattr(settings.database, 'path'):
            db_path = settings.database.path
            print_info(f"Database path: {db_path}")
        
        # Cek log dir
        if hasattr(settings, 'logging') and hasattr(settings.logging, 'log_dir'):
            log_dir = settings.logging.log_dir
            print_info(f"Log directory: {log_dir}")
            # Buat direktori jika belum ada
            log_dir.mkdir(parents=True, exist_ok=True)
            print_success(f"Log directory created/verified")
        
        return True
    except ImportError as e:
        print_error(f"config import error: {e}")
        return False
    except Exception as e:
        print_error(f"config error: {e}")
        return False


def check_database():
    """Cek database module"""
    print_header("DATABASE")
    
    all_ok = True
    
    # Cek database.models
    if check_import("database.models", "Constants", silent=True):
        print_success("database.models with Constants")
    else:
        print_error("database.models missing Constants")
        all_ok = False
    
    # Cek database.connection
    if check_import("database.connection", "init_db", silent=True):
        print_success("database.connection with init_db")
    else:
        print_error("database.connection missing init_db")
        all_ok = False
    
    return all_ok


def check_utils():
    """Cek utils modules"""
    print_header("UTILITIES")
    
    all_ok = True
    
    # Logger
    if check_import("utils.logger", "setup_logging", silent=True):
        print_success("utils.logger with setup_logging")
    else:
        print_error("utils.logger missing setup_logging")
        all_ok = False
    
    if check_import("utils.logger", "logger", silent=True):
        print_success("utils.logger with logger")
    else:
        print_warning("utils.logger missing logger (might be alias)")
    
    # Exceptions
    if check_import("utils.exceptions", "MyLoveError", silent=True):
        print_success("utils.exceptions with MyLoveError")
    else:
        print_warning("utils.exceptions missing MyLoveError")
    
    if check_import("utils.exceptions", "GadisBaseException", silent=True):
        print_success("utils.exceptions with GadisBaseException (alias)")
    else:
        print_warning("utils.exceptions missing GadisBaseException")
    
    # Helpers
    if check_import("utils.helpers", "sanitize_input", silent=True):
        print_success("utils.helpers available")
    else:
        print_warning("utils.helpers not available (optional)")
    
    return all_ok


def check_bot_modules():
    """Cek bot modules"""
    print_header("BOT MODULES")
    
    all_ok = True
    
    # Bot package
    if check_import("bot", "create_application", silent=True):
        print_success("bot.create_application")
    else:
        print_warning("bot.create_application not directly exported")
    
    # Bot handlers - cek beberapa command penting
    important_handlers = [
        'start_command',
        'help_command',
        'status_command',
        'cancel_command',
        'message_handler',
        'callback_handler',
        'hts_call_handler',
        'fwb_call_handler',
    ]
    
    for handler in important_handlers:
        if check_import("bot.handlers", handler, silent=True):
            print_info(f"bot.handlers.{handler} OK")
        else:
            print_error(f"bot.handlers.{handler} MISSING")
            all_ok = False
    
    # Bot callbacks
    important_callbacks = [
        'agree_18_callback',
        'role_ipar_callback',
        'role_teman_kantor_callback',
        'role_janda_callback',
        'role_pelakor_callback',
        'role_istri_orang_callback',
        'role_pdkt_callback',
        'role_sepupu_callback',
        'role_teman_sma_callback',
        'role_mantan_callback',
        'end_callback',
        'close_callback',
        'jadipacar_callback',
        'break_callback',
        'breakup_callback',
        'fwb_callback',
    ]
    
    for callback in important_callbacks:
        if check_import("bot.callbacks", callback, silent=True):
            print_info(f"bot.callbacks.{callback} OK")
        else:
            print_error(f"bot.callbacks.{callback} MISSING")
            all_ok = False
    
    # Bot commands
    if check_import("bot.commands", "error_handler", silent=True):
        print_info("bot.commands.error_handler OK")
    else:
        print_error("bot.commands.error_handler MISSING")
        all_ok = False
    
    # Bot webhook
    if check_import("bot.webhook", "setup_webhook_sync", silent=True):
        print_info("bot.webhook.setup_webhook_sync OK")
    else:
        print_warning("bot.webhook.setup_webhook_sync not found")
    
    return all_ok


def check_cache():
    """Cek cache module"""
    print_header("CACHE")
    
    # Cache is optional, only warn if missing
    if check_import("cache", "__init__", silent=True):
        print_success("cache module exists")
        if check_import("cache.redis_client", "init_redis", silent=True):
            print_info("cache.redis_client.init_redis OK")
        else:
            print_warning("cache.redis_client missing init_redis")
    else:
        print_warning("cache module not found (optional)")
    
    return True


def check_public_modules():
    """Cek public modules (opsional)"""
    print_header("PUBLIC MODULES")
    
    # Public modules are optional, only warn if missing
    modules = [
        ('public.locations', 'PublicLocations'),
        ('public.risk', 'RiskCalculator'),
        ('session.unique_id', 'id_generator'),
        ('roles.artis_references', 'get_random_artist_for_role'),
        ('threesome.manager', 'ThreesomeManager'),
    ]
    
    for module, attr in modules:
        if check_import(module, attr, silent=True):
            print_info(f"{module}.{attr} OK")
        else:
            print_warning(f"{module}.{attr} not found (optional)")
    
    return True


def check_healthcheck():
    """Cek healthcheck server"""
    print_header("HEALTHCHECK")
    
    # Cek Flask
    if check_import("flask", "Flask", silent=True):
        print_success("Flask installed for healthcheck")
        print_info("Healthcheck endpoint akan tersedia di /health")
    else:
        print_warning("Flask not installed - healthcheck disabled")
        print_info("Install dengan: pip install flask")
    
    # Cek PORT environment
    port = os.getenv('PORT', '8080')
    print_info(f"PORT: {port}")
    
    return True


def check_main():
    """Cek main.py bisa diimport"""
    print_header("MAIN MODULE")
    
    try:
        import main
        print_success("main.py imported")
        
        # Cek fungsi utama ada
        if hasattr(main, 'main'):
            print_info("main.main() function exists")
        else:
            print_error("main.main() function missing")
            return False
        
        return True
    except ImportError as e:
        print_error(f"main.py import error: {e}")
        return False
    except Exception as e:
        print_error(f"main.py error: {e}")
        return False


def main():
    """Main function"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔍 MYLOVE ULTIMATE VERSI 1 - DEPLOYMENT CHECK{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    print_info(f"Python version: {sys.version}")
    print_info(f"Working directory: {ROOT_DIR}")
    print()
    
    checks = [
        check_environment_variables,
        check_dependencies,
        check_config,
        check_database,
        check_utils,
        check_bot_modules,
        check_cache,
        check_public_modules,
        check_healthcheck,
        check_main,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print_error(f"Error in {check.__name__}: {e}")
            results.append(False)
    
    print_header("SUMMARY")
    
    total_checks = len(results)
    passed = sum(results)
    failed = total_checks - passed
    
    if failed == 0:
        print_success(f"✅ ALL CHECKS PASSED ({passed}/{total_checks})")
        print(f"\n{GREEN}🚀 Siap deploy ke Railway!{RESET}")
        return 0
    else:
        print_warning(f"⚠️  {failed} check(s) failed ({passed}/{total_checks})")
        print(f"\n{YELLOW}Perbaiki error di atas sebelum deploy!{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
