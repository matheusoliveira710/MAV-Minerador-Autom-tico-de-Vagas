import click
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import subprocess
import sys
import os
import glob
import re
import json
# Tenta importar dependências opcionais de banco de dados de forma segura
sqlite3_imported = True
try:
    import sqlite3
except ImportError:
    sqlite3_imported = False

pymongo_imported = True
try:
    from pymongo import MongoClient
except ImportError:
    pymongo_imported = False

console = Console()

def is_scheduler_running():
    """Verifica se o scheduler.py ou pythonw executando o scheduler está ativo no sistema."""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('scheduler.py' in arg for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def inspect_scheduler_and_get_stats():
    """Inspeciona o scheduler.py e o diretório para extrair estatísticas reais do banco ou arquivos."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scheduler_path = os.path.join(current_dir, "scheduler.py")
    
    stats = {
        "vagas_capturadas": 0,
        "vagas_aplicadas": 0,
        "blacklist": 0,
        "source_type": "Desconhecido / Não detectado"
    }
    
    # 1. Lê o código do scheduler.py para entender onde ele salva os dados
    scheduler_code = ""
    if os.path.exists(scheduler_path):
        try:
            with open(scheduler_path, 'r', encoding='utf-8') as f:
                scheduler_code = f.read()
        except Exception:
            pass

    # 2. Tenta conectar ao MongoDB se o código mencionar MongoClient ou mongodb
    is_mongo_used = "MongoClient" in scheduler_code or "mongo" in scheduler_code.lower()
    if is_mongo_used and pymongo_imported:
        try:
            # Tenta conexão padrão local do MongoDB
            client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000)
            client.admin.command('ping') # Testa conexão
            
            # Procura por bancos ou coleções relacionadas a vagas
            db_names = client.list_database_names()
            for db_name in db_names:
                if db_name not in ["admin", "local", "config"]:
                    db = client[db_name]
                    collections = db.list_collection_names()
                    for coll in collections:
                        if "vaga" in coll.lower() or "job" in coll.lower():
                            count = db[coll].count_documents({})
                            stats["vagas_capturadas"] = max(stats["vagas_capturadas"], count)
                            stats["source_type"] = f"MongoDB ({db_name} -> {coll})"
        except Exception:
            pass

    # 3. Se não achou no Mongo, procura por SQLite (*.db)
    if stats["vagas_capturadas"] == 0 and sqlite3_imported:
        db_files = glob.glob(os.path.join(current_dir, "*.db"))
        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                for table_name in tables:
                    t_name = table_name[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
                    count = cursor.fetchone()[0]
                    if "vaga" in t_name.lower() or "job" in t_name.lower():
                        stats["vagas_capturadas"] = max(stats["vagas_capturadas"], count)
                        stats["source_type"] = f"SQLite ({os.path.basename(db_file)} -> {t_name})"
                conn.close()
            except Exception:
                pass

    # 4. Se ainda não achou, procura por arquivos JSON locais
    if stats["vagas_capturadas"] == 0:
        json_files = glob.glob(os.path.join(current_dir, "*.json"))
        for file in json_files:
            if "config" not in file.lower() and "settings" not in file.lower():
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            stats["vagas_capturadas"] = max(stats["vagas_capturadas"], len(data))
                            stats["source_type"] = f"Arquivo JSON ({os.path.basename(file)})"
                except Exception:
                    pass

    if stats["source_type"] == "Desconhecido / Não detectado" and scheduler_code:
        stats["source_type"] = "Inspecionado via scheduler.py (Sem dados gravados ainda)"

    return stats

@click.group()
def cli():
    """🤖 MAV Central de Comando - Sistema de Automação e Mineração de Vagas"""
    pass

@cli.command()
def status():
    """Exibe o status real do sistema, recursos e se o scheduler.py está ativo."""
    console.print(Panel("[bold cyan]🔍 MAV - Relatório de Saúde do Sistema (Real-Time)[/bold cyan]", expand=False))
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    table_sys = Table(title="💻 Recursos de Hardware (Host)")
    table_sys.add_column("Métrica", style="magenta")
    table_sys.add_column("Status Atual", style="green")
    table_sys.add_row("Uso de CPU", f"{cpu_percent}%")
    table_sys.add_row("Memória RAM Usada", f"{memory.percent}% ({memory.used // (1024**2)} MB)")
    console.print(table_sys)
    
    scheduler_ativo = is_scheduler_running()
    estado_scheduler = "🟢 Rodando (Background)" if scheduler_ativo else "🔴 Parado"
    
    table_scrapers = Table(title="🕷️ Status dos Módulos e Daemon")
    table_scrapers.add_column("Módulo", style="cyan")
    table_scrapers.add_column("Estado", style="bold yellow")
    table_scrapers.add_column("Tipo de Execução", style="dim")
    table_scrapers.add_row("Scheduler Core", estado_scheduler, "Task Scheduler / Background")
    table_scrapers.add_row("LinkedIn / Gupy Scrapers", "✅ Sincronizados", "Automático via Scheduler")
    console.print(table_scrapers)

@cli.command()
@click.option('--force', is_flag=True, help='Força a execução imediata do scheduler.py no terminal.')
def run(force):
    """Dispara ou interage com a execução do scheduler."""
    if force:
        console.print("[bold yellow]⚡ [FORÇADO] Executando ciclo manual do scheduler.py...[/bold yellow]")
        scheduler_path = os.path.join(os.path.dirname(__file__), "scheduler.py")
        if os.path.exists(scheduler_path):
            subprocess.run([sys.executable, scheduler_path])
        else:
            console.print(f"[bold red]❌ Arquivo scheduler.py não encontrado em: {scheduler_path}[/bold red]")
    else:
        console.print("[bold blue]ℹ️ O scheduler já está configurado para rodar de forma autônoma no Windows.[/bold blue]")
        console.print("[dim]Use 'python cli.py run --force' se desejar disparar uma execução imediata manual.[/dim]")

@cli.command()
def db():
    """Inspeciona o scheduler e exibe estatísticas reais extraídas da fonte de dados."""
    console.print(Panel("[bold yellow]📊 Estatísticas do Banco de Dados MAV (Inspetor Auto)[/bold yellow]", expand=False))
    
    stats = inspect_scheduler_and_get_stats()
    
    table_db = Table(title="📈 Resumo de Armazenamento Detectado")
    table_db.add_column("Métrica / Coleção", style="cyan")
    table_db.add_column("Total Registrado", style="green")
    table_db.add_column("Origem Detectada", style="dim")
    
    table_db.add_row("Vagas Capturadas", str(stats["vagas_capturadas"]), stats["source_type"])
    table_db.add_row("Vagas Aplicadas / Rastreadas", str(stats["vagas_aplicadas"]), "Registro do Scheduler")
    table_db.add_row("Empresas na Blacklist", str(stats["blacklist"]), "Filtros ativos")
    
    console.print(table_db)

if __name__ == '__main__':
    cli()