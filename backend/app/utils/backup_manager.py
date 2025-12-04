"""
Script para backup automático do ChromaDB.
Cria backups comprimidos com timestamp e gerencia rotação de backups antigos.
"""

import os
import shutil
import tarfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChromaDBBackup:
    """Gerenciador de backups do ChromaDB"""
    
    def __init__(
        self,
        chroma_db_path: str,
        backup_dir: str,
        max_backups: int = 7,
        compression: str = "gz"
    ):
        """
        Args:
            chroma_db_path: Caminho para o diretório ChromaDB
            backup_dir: Diretório onde salvar backups
            max_backups: Número máximo de backups a manter
            compression: Tipo de compressão (gz, bz2, xz)
        """
        self.chroma_db_path = Path(chroma_db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.compression = compression
        
        # Cria diretório de backup se não existir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ChromaDBBackup inicializado:")
        logger.info(f"  - DB Path: {self.chroma_db_path}")
        logger.info(f"  - Backup Dir: {self.backup_dir}")
        logger.info(f"  - Max Backups: {self.max_backups}")
    
    def create_backup(self, description: Optional[str] = None) -> Path:
        """
        Cria um backup do ChromaDB.
        
        Args:
            description: Descrição opcional do backup
            
        Returns:
            Caminho do arquivo de backup criado
        """
        if not self.chroma_db_path.exists():
            raise FileNotFoundError(f"ChromaDB não encontrado em {self.chroma_db_path}")
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"chromadb_backup_{timestamp}"
        
        if description:
            # Sanitiza descrição
            safe_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_desc = safe_desc.replace(' ', '_')[:50]
            backup_name = f"{backup_name}_{safe_desc}"
        
        backup_file = self.backup_dir / f"{backup_name}.tar.{self.compression}"
        
        logger.info(f"Criando backup: {backup_file.name}")
        logger.info(f"Comprimindo {self.chroma_db_path}...")
        
        try:
            # Cria arquivo tar comprimido
            with tarfile.open(backup_file, f"w:{self.compression}") as tar:
                tar.add(
                    self.chroma_db_path,
                    arcname=self.chroma_db_path.name,
                    filter=self._tar_filter
                )
            
            # Obtém tamanho do backup
            backup_size = backup_file.stat().st_size
            backup_size_mb = backup_size / (1024 * 1024)
            
            logger.info(f"✓ Backup criado com sucesso: {backup_file.name}")
            logger.info(f"  Tamanho: {backup_size_mb:.2f} MB")
            
            return backup_file
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            # Remove arquivo parcial se houver erro
            if backup_file.exists():
                backup_file.unlink()
            raise
    
    def restore_backup(self, backup_file: Path, target_path: Optional[Path] = None) -> Path:
        """
        Restaura um backup.
        
        Args:
            backup_file: Caminho do arquivo de backup
            target_path: Caminho de destino (usa chroma_db_path se None)
            
        Returns:
            Caminho do diretório restaurado
        """
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup não encontrado: {backup_file}")
        
        target = target_path or self.chroma_db_path
        
        logger.info(f"Restaurando backup: {backup_file.name}")
        logger.info(f"Destino: {target}")
        
        # Cria backup do estado atual antes de restaurar
        if target.exists():
            logger.warning(f"Destino já existe. Criando backup de segurança...")
            safety_backup = self.backup_dir / f"safety_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            with tarfile.open(safety_backup, "w:gz") as tar:
                tar.add(target, arcname=target.name)
            logger.info(f"Backup de segurança criado: {safety_backup.name}")
            
            # Remove diretório atual
            shutil.rmtree(target)
        
        try:
            # Extrai backup
            with tarfile.open(backup_file, f"r:{self.compression}") as tar:
                tar.extractall(target.parent)
            
            logger.info(f"✓ Backup restaurado com sucesso em {target}")
            return target
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            raise
    
    def list_backups(self) -> list:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            Lista de dicionários com informações dos backups
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("chromadb_backup_*.tar.*"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": stat.st_size / (1024 * 1024),
                "created_at": datetime.fromtimestamp(stat.st_mtime),
                "age_days": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
            })
        
        return backups
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backups antigos mantendo apenas max_backups.
        
        Returns:
            Número de backups removidos
        """
        backups = self.list_backups()
        
        if len(backups) <= self.max_backups:
            logger.info(f"Nenhum backup para remover ({len(backups)}/{self.max_backups})")
            return 0
        
        to_remove = backups[self.max_backups:]
        removed_count = 0
        
        for backup in to_remove:
            backup_path = Path(backup["path"])
            logger.info(f"Removendo backup antigo: {backup['filename']} ({backup['age_days']} dias)")
            backup_path.unlink()
            removed_count += 1
        
        logger.info(f"✓ {removed_count} backup(s) antigo(s) removido(s)")
        return removed_count
    
    def _tar_filter(self, tarinfo):
        """Filtro para excluir arquivos temporários do backup"""
        exclude_patterns = ['.tmp', '.temp', '__pycache__', '.pyc']
        
        if any(pattern in tarinfo.name for pattern in exclude_patterns):
            return None
        
        return tarinfo
    
    def get_stats(self) -> dict:
        """Retorna estatísticas dos backups"""
        backups = self.list_backups()
        
        total_size = sum(b['size_mb'] for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size_mb": round(total_size, 2),
            "oldest_backup": backups[-1]['created_at'].isoformat() if backups else None,
            "newest_backup": backups[0]['created_at'].isoformat() if backups else None,
            "max_backups": self.max_backups,
            "backup_dir": str(self.backup_dir)
        }


def main():
    """CLI para gerenciamento de backups"""
    parser = argparse.ArgumentParser(description="Gerenciador de backups ChromaDB")
    parser.add_argument(
        "action",
        choices=["create", "list", "cleanup", "restore", "stats"],
        help="Ação a executar"
    )
    parser.add_argument(
        "--db-path",
        default="db_migration/chroma_db",
        help="Caminho para ChromaDB"
    )
    parser.add_argument(
        "--backup-dir",
        default="backups",
        help="Diretório de backups"
    )
    parser.add_argument(
        "--max-backups",
        type=int,
        default=7,
        help="Número máximo de backups"
    )
    parser.add_argument(
        "--description",
        help="Descrição do backup"
    )
    parser.add_argument(
        "--backup-file",
        help="Arquivo de backup para restaurar"
    )
    
    args = parser.parse_args()
    
    # Inicializa gerenciador
    backup_manager = ChromaDBBackup(
        chroma_db_path=args.db_path,
        backup_dir=args.backup_dir,
        max_backups=args.max_backups
    )
    
    try:
        if args.action == "create":
            backup_file = backup_manager.create_backup(description=args.description)
            backup_manager.cleanup_old_backups()
            print(f"\n✓ Backup criado: {backup_file}")
        
        elif args.action == "list":
            backups = backup_manager.list_backups()
            print(f"\n📦 Backups disponíveis ({len(backups)}):\n")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']}")
                print(f"   Tamanho: {backup['size_mb']:.2f} MB")
                print(f"   Criado: {backup['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Idade: {backup['age_days']} dias\n")
        
        elif args.action == "cleanup":
            removed = backup_manager.cleanup_old_backups()
            print(f"\n✓ {removed} backup(s) removido(s)")
        
        elif args.action == "restore":
            if not args.backup_file:
                print("❌ Erro: --backup-file é obrigatório para restore")
                return
            
            backup_path = Path(args.backup_file)
            restored_path = backup_manager.restore_backup(backup_path)
            print(f"\n✓ Backup restaurado em: {restored_path}")
        
        elif args.action == "stats":
            stats = backup_manager.get_stats()
            print(f"\n📊 Estatísticas de Backup:\n")
            print(f"Total de backups: {stats['total_backups']}")
            print(f"Tamanho total: {stats['total_size_mb']} MB")
            print(f"Diretório: {stats['backup_dir']}")
            print(f"Limite: {stats['max_backups']} backups")
            if stats['newest_backup']:
                print(f"Mais recente: {stats['newest_backup']}")
            if stats['oldest_backup']:
                print(f"Mais antigo: {stats['oldest_backup']}")
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
