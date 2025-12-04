"""
Sistema de métricas para monitoramento de performance.
Compatível com Prometheus e pode ser expandido para outros sistemas.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Coletor de métricas centralizado.
    Armazena contadores, histogramas e gauges em memória.
    """
    
    def __init__(self):
        self._lock = Lock()
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._timings: Dict[str, list] = defaultdict(list)
        self._labels: Dict[str, Dict[str, Any]] = {}
        
        logger.info("MetricsCollector inicializado")
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """
        Incrementa um contador.
        
        Args:
            name: Nome da métrica
            value: Valor a incrementar
            labels: Labels adicionais para a métrica
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            if labels:
                self._labels[key] = labels
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Define um valor gauge (pode subir ou descer).
        
        Args:
            name: Nome da métrica
            value: Valor atual
            labels: Labels adicionais
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Adiciona uma observação a um histograma.
        
        Args:
            name: Nome da métrica
            value: Valor observado
            labels: Labels adicionais
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            # Mantém apenas as últimas 1000 observações
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
            if labels:
                self._labels[key] = labels
    
    def record_timing(self, name: str, duration_seconds: float, labels: Optional[Dict[str, str]] = None):
        """
        Registra tempo de execução.
        
        Args:
            name: Nome da operação
            duration_seconds: Duração em segundos
            labels: Labels adicionais
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._timings[key].append(duration_seconds)
            # Mantém apenas os últimos 1000 registros
            if len(self._timings[key]) > 1000:
                self._timings[key] = self._timings[key][-1000:]
            if labels:
                self._labels[key] = labels
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna todas as métricas coletadas.
        
        Returns:
            Dicionário com todas as métricas
        """
        with self._lock:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": self._calculate_histogram_stats(),
                "timings": self._calculate_timing_stats()
            }
            return metrics
    
    def get_prometheus_format(self) -> str:
        """
        Retorna métricas no formato Prometheus.
        
        Returns:
            String formatada para Prometheus
        """
        lines = []
        
        # Counters
        for name, value in self._counters.items():
            metric_name = name.replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {metric_name} counter")
            lines.append(f"{metric_name} {value}")
        
        # Gauges
        for name, value in self._gauges.items():
            metric_name = name.replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f"{metric_name} {value}")
        
        # Histograms (simplificado)
        for name, values in self._histograms.items():
            if values:
                metric_name = name.replace(".", "_").replace("-", "_")
                lines.append(f"# TYPE {metric_name} histogram")
                lines.append(f"{metric_name}_sum {sum(values)}")
                lines.append(f"{metric_name}_count {len(values)}")
                lines.append(f"{metric_name}_avg {sum(values)/len(values)}")
        
        return "\n".join(lines) + "\n"
    
    def _calculate_histogram_stats(self) -> Dict[str, Dict[str, float]]:
        """Calcula estatísticas para histogramas"""
        stats = {}
        for name, values in self._histograms.items():
            if values:
                sorted_values = sorted(values)
                count = len(sorted_values)
                stats[name] = {
                    "count": count,
                    "sum": sum(sorted_values),
                    "min": sorted_values[0],
                    "max": sorted_values[-1],
                    "avg": sum(sorted_values) / count,
                    "p50": sorted_values[int(count * 0.5)],
                    "p95": sorted_values[int(count * 0.95)],
                    "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[-1]
                }
        return stats
    
    def _calculate_timing_stats(self) -> Dict[str, Dict[str, float]]:
        """Calcula estatísticas para timings"""
        stats = {}
        for name, values in self._timings.items():
            if values:
                sorted_values = sorted(values)
                count = len(sorted_values)
                stats[name] = {
                    "count": count,
                    "total_seconds": sum(sorted_values),
                    "min_seconds": sorted_values[0],
                    "max_seconds": sorted_values[-1],
                    "avg_seconds": sum(sorted_values) / count,
                    "p50_seconds": sorted_values[int(count * 0.5)],
                    "p95_seconds": sorted_values[int(count * 0.95)],
                    "p99_seconds": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[-1]
                }
        return stats
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Cria chave única para métrica com labels"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def reset(self):
        """Reseta todas as métricas"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timings.clear()
            self._labels.clear()
            logger.warning("Métricas resetadas")


class Timer:
    """Context manager para medir tempo de execução"""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, labels: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.collector.record_timing(self.metric_name, duration, self.labels)
        return False


# Instância global
metrics_collector = MetricsCollector()
