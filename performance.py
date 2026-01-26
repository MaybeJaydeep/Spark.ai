#!/usr/bin/env python3
"""
Performance Monitoring and Optimization Module

Provides performance tracking, profiling, and optimization utilities.
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    timestamp: float
    unit: str = "seconds"
    category: str = "general"


class PerformanceMonitor:
    """
    Performance monitoring system for tracking system and application metrics
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.active_timers = {}
        self.counters = defaultdict(int)
        self.lock = threading.Lock()
        
        # System monitoring
        self.system_metrics_enabled = True
        self.system_monitor_interval = 5.0  # seconds
        self.system_monitor_thread = None
        self.monitoring_active = False
    
    def start_timer(self, name: str) -> str:
        """
        Start a performance timer
        
        Args:
            name: Timer name
            
        Returns:
            Timer ID for stopping
        """
        timer_id = f"{name}_{time.time()}"
        with self.lock:
            self.active_timers[timer_id] = {
                'name': name,
                'start_time': time.time(),
                'thread_id': threading.get_ident()
            }
        return timer_id
    
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """
        Stop a performance timer
        
        Args:
            timer_id: Timer ID from start_timer
            
        Returns:
            Duration in seconds, or None if timer not found
        """
        with self.lock:
            if timer_id in self.active_timers:
                timer_info = self.active_timers.pop(timer_id)
                duration = time.time() - timer_info['start_time']
                
                # Record metric
                metric = PerformanceMetric(
                    name=timer_info['name'],
                    value=duration,
                    timestamp=time.time(),
                    unit="seconds",
                    category="timing"
                )
                self.metrics[timer_info['name']].append(metric)
                
                return duration
        return None
    
    @contextmanager
    def timer(self, name: str):
        """
        Context manager for timing operations
        
        Args:
            name: Timer name
            
        Usage:
            with monitor.timer("operation_name"):
                # code to time
        """
        timer_id = self.start_timer(name)
        try:
            yield
        finally:
            self.stop_timer(timer_id)
    
    def record_metric(self, name: str, value: float, unit: str = "count", category: str = "general"):
        """
        Record a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            category: Metric category
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=time.time(),
            unit=unit,
            category=category
        )
        
        with self.lock:
            self.metrics[name].append(metric)
    
    def increment_counter(self, name: str, value: int = 1):
        """
        Increment a counter metric
        
        Args:
            name: Counter name
            value: Increment value
        """
        with self.lock:
            self.counters[name] += value
    
    def get_metric_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a metric
        
        Args:
            name: Metric name
            
        Returns:
            Dictionary of statistics
        """
        with self.lock:
            if name not in self.metrics:
                return {}
            
            values = [m.value for m in self.metrics[name]]
            
            if not values:
                return {}
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'average': sum(values) / len(values),
                'latest': values[-1],
                'total': sum(values)
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system performance metrics
        
        Returns:
            Dictionary of system metrics
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            except:
                network_stats = {}
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_average': getattr(psutil, 'getloadavg', lambda: [0, 0, 0])()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': network_stats,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {'error': str(e), 'timestamp': time.time()}
    
    def start_system_monitoring(self):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.system_monitor_thread = threading.Thread(
            target=self._system_monitor_loop,
            daemon=True
        )
        self.system_monitor_thread.start()
    
    def stop_system_monitoring(self):
        """Stop continuous system monitoring"""
        self.monitoring_active = False
        if self.system_monitor_thread:
            self.system_monitor_thread.join(timeout=1.0)
    
    def _system_monitor_loop(self):
        """System monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self.get_system_metrics()
                
                # Record system metrics
                if 'error' not in metrics:
                    self.record_metric('cpu_percent', metrics['cpu']['percent'], 'percent', 'system')
                    self.record_metric('memory_percent', metrics['memory']['percent'], 'percent', 'system')
                    self.record_metric('disk_percent', metrics['disk']['percent'], 'percent', 'system')
                
                time.sleep(self.system_monitor_interval)
                
            except Exception as e:
                print(f"System monitoring error: {e}")
                time.sleep(self.system_monitor_interval)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Returns:
            Performance report dictionary
        """
        with self.lock:
            report = {
                'timestamp': time.time(),
                'active_timers': len(self.active_timers),
                'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
                'counters': dict(self.counters),
                'metric_stats': {},
                'system_metrics': self.get_system_metrics() if self.system_metrics_enabled else {}
            }
            
            # Get stats for all metrics
            for name in self.metrics:
                report['metric_stats'][name] = self.get_metric_stats(name)
            
            return report
    
    def clear_metrics(self, older_than: float = None):
        """
        Clear metrics, optionally only those older than specified time
        
        Args:
            older_than: Clear metrics older than this timestamp
        """
        with self.lock:
            if older_than is None:
                self.metrics.clear()
                self.counters.clear()
            else:
                for name, metric_list in self.metrics.items():
                    # Keep only recent metrics
                    recent_metrics = deque(maxlen=self.max_history)
                    for metric in metric_list:
                        if metric.timestamp >= older_than:
                            recent_metrics.append(metric)
                    self.metrics[name] = recent_metrics


class PerformanceProfiler:
    """
    Code profiler for detailed performance analysis
    """
    
    def __init__(self):
        self.profiles = {}
        self.active_profiles = {}
    
    def profile_function(self, func: Callable) -> Callable:
        """
        Decorator to profile function execution
        
        Args:
            func: Function to profile
            
        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                # Record profile data
                func_name = f"{func.__module__}.{func.__name__}"
                if func_name not in self.profiles:
                    self.profiles[func_name] = []
                
                self.profiles[func_name].append({
                    'duration': duration,
                    'timestamp': start_time,
                    'success': success,
                    'error': error,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
            
            return result
        
        return wrapper
    
    def get_profile_stats(self, func_name: str) -> Dict[str, Any]:
        """
        Get profiling statistics for a function
        
        Args:
            func_name: Function name
            
        Returns:
            Profile statistics
        """
        if func_name not in self.profiles:
            return {}
        
        profiles = self.profiles[func_name]
        durations = [p['duration'] for p in profiles]
        successes = [p['success'] for p in profiles]
        
        return {
            'call_count': len(profiles),
            'total_time': sum(durations),
            'average_time': sum(durations) / len(durations),
            'min_time': min(durations),
            'max_time': max(durations),
            'success_rate': sum(successes) / len(successes) * 100,
            'last_called': max(p['timestamp'] for p in profiles)
        }


# Global instances
_performance_monitor: Optional[PerformanceMonitor] = None
_performance_profiler: Optional[PerformanceProfiler] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_performance_profiler() -> PerformanceProfiler:
    """Get the global performance profiler instance"""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler


# Convenience decorators and functions
def timed(name: str = None):
    """
    Decorator to time function execution
    
    Args:
        name: Optional timer name (defaults to function name)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            timer_name = name or f"{func.__module__}.{func.__name__}"
            monitor = get_performance_monitor()
            
            with monitor.timer(timer_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def profiled(func):
    """Decorator to profile function execution"""
    profiler = get_performance_profiler()
    return profiler.profile_function(func)


if __name__ == "__main__":
    # Test performance monitoring
    print("📊 Testing Performance Monitoring")
    print("=" * 40)
    
    monitor = PerformanceMonitor()
    
    # Test timing
    print("\n⏱️  Testing Timing:")
    with monitor.timer("test_operation"):
        time.sleep(0.1)
    
    # Test metrics
    monitor.record_metric("test_metric", 42.0, "units", "test")
    monitor.increment_counter("test_counter", 5)
    
    # Get stats
    stats = monitor.get_metric_stats("test_operation")
    print(f"Test operation stats: {stats}")
    
    # Test system metrics
    print("\n🖥️  System Metrics:")
    sys_metrics = monitor.get_system_metrics()
    if 'error' not in sys_metrics:
        print(f"CPU: {sys_metrics['cpu']['percent']:.1f}%")
        print(f"Memory: {sys_metrics['memory']['percent']:.1f}%")
        print(f"Disk: {sys_metrics['disk']['percent']:.1f}%")
    
    # Test profiler
    print("\n🔍 Testing Profiler:")
    profiler = PerformanceProfiler()
    
    @profiler.profile_function
    def test_function(x):
        time.sleep(0.05)
        return x * 2
    
    # Call function multiple times
    for i in range(3):
        test_function(i)
    
    # Get profile stats
    stats = profiler.get_profile_stats("__main__.test_function")
    print(f"Function profile: {stats}")
    
    print("\n✅ Performance monitoring working!")