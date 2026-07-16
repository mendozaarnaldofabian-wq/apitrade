"""
Generador de señales - Reglas configurables para generar señales de trading
"""
import logging
from enum import Enum
from typing import Dict, List
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Tipos de señales"""
    BUY = "BUY"      # Señal para comprar (CALL)
    SELL = "SELL"    # Señal para vender (PUT)
    HOLD = "HOLD"    # Mantener posición
    CLOSE = "CLOSE"  # Cerrar posición


class SignalStrength(Enum):
    """Fortaleza de la señal"""
    WEAK = 1
    MEDIUM = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class Signal:
    """Representa una señal de trading"""
    signal_type: SignalType
    strength: SignalStrength
    confidence: float  # 0 a 1
    reasons: List[str]
    timestamp: str
    indicators_used: Dict
    
    def to_dict(self) -> Dict:
        """Convierte la señal a diccionario"""
        return {
            'type': self.signal_type.value,
            'strength': self.strength.name,
            'confidence': f"{self.confidence:.2%}",
            'reasons': self.reasons,
            'timestamp': self.timestamp,
            'indicators': self.indicators_used
        }


class SignalGenerator:
    """Genera señales de trading basadas en reglas configurables"""
    
    def __init__(self, config: Dict = None):
        """
        Inicializa el generador de señales
        
        Args:
            config (Dict): Configuración de las reglas
        """
        self.config = config or self.get_default_config()
        self.signals_history = []
    
    @staticmethod
    def get_default_config() -> Dict:
        """Retorna configuración por defecto"""
        return {
            'rsi': {
                'enabled': True,
                'overbought': 70,
                'oversold': 30,
                'period': 14
            },
            'macd': {
                'enabled': True,
                'fast': 12,
                'slow': 26,
                'signal': 9
            },
            'bollinger': {
                'enabled': True,
                'period': 20,
                'std_dev': 2.0
            },
            'moving_averages': {
                'enabled': True,
                'fast_period': 20,
                'slow_period': 50
            },
            'atr': {
                'enabled': True,
                'period': 14
            },
            'adx': {
                'enabled': True,
                'period': 14,
                'strong_trend': 25
            },
            'min_confidence': 0.5  # Confianza mínima para generar señal
        }
    
    def update_config(self, new_config: Dict):
        """
        Actualiza la configuración
        
        Args:
            new_config (Dict): Nueva configuración
        """
        self.config.update(new_config)
        logger.info(f"✓ Configuración actualizada")
    
    def generate_signal(self, analyzer) -> Signal:
        """
        Genera una señal basada en los indicadores del analizador
        
        Args:
            analyzer: Instancia de CandleAnalyzer con indicadores calculados
            
        Returns:
            Signal: Señal generada
        """
        reasons = []
        scores = {'buy': 0, 'sell': 0}
        indicators_used = {}
        
        # ============ RSI ============
        if self.config['rsi']['enabled']:
            rsi = analyzer.indicators.get('RSI', None)
            if rsi is not None:
                last_rsi = rsi.iloc[-1]
                indicators_used['RSI'] = round(last_rsi, 2)
                
                if last_rsi < self.config['rsi']['oversold']:
                    scores['buy'] += 2
                    reasons.append(f"RSI sobrevendido ({last_rsi:.1f})")
                elif last_rsi > self.config['rsi']['overbought']:
                    scores['sell'] += 2
                    reasons.append(f"RSI sobrecomprado ({last_rsi:.1f})")
        
        # ============ MACD ============
        if self.config['macd']['enabled']:
            macd = analyzer.indicators.get('MACD', None)
            signal_line = analyzer.indicators.get('MACD_Signal', None)
            histogram = analyzer.indicators.get('MACD_Histogram', None)
            
            if macd is not None and signal_line is not None:
                last_macd = macd.iloc[-1]
                last_signal = signal_line.iloc[-1]
                last_histogram = histogram.iloc[-1]
                
                indicators_used['MACD'] = round(last_macd, 5)
                indicators_used['MACD_Signal'] = round(last_signal, 5)
                
                # Verificar cruce de MACD
                if len(macd) > 1:
                    prev_macd = macd.iloc[-2]
                    prev_signal = signal_line.iloc[-2]
                    
                    # MACD cruza hacia arriba la línea de señal
                    if prev_macd <= prev_signal and last_macd > last_signal:
                        scores['buy'] += 2
                        reasons.append("MACD cruce alcista")
                    # MACD cruza hacia abajo la línea de señal
                    elif prev_macd >= prev_signal and last_macd < last_signal:
                        scores['sell'] += 2
                        reasons.append("MACD cruce bajista")
        
        # ============ BOLLINGER BANDS ============
        if self.config['bollinger']['enabled']:
            bb_upper = analyzer.indicators.get('BB_Upper', None)
            bb_lower = analyzer.indicators.get('BB_Lower', None)
            
            if bb_upper is not None and bb_lower is not None:
                last_close = analyzer.df['close'].iloc[-1]
                last_upper = bb_upper.iloc[-1]
                last_lower = bb_lower.iloc[-1]
                
                indicators_used['BB_Upper'] = round(last_upper, 5)
                indicators_used['BB_Lower'] = round(last_lower, 5)
                
                if last_close < last_lower:
                    scores['buy'] += 1
                    reasons.append("Precio bajo banda inferior")
                elif last_close > last_upper:
                    scores['sell'] += 1
                    reasons.append("Precio sobre banda superior")
        
        # ============ MEDIA MÓVILES ============
        if self.config['moving_averages']['enabled']:
            ema_fast = analyzer.indicators.get('EMA_20', None)
            ema_slow = analyzer.indicators.get('EMA_50', None)
            
            if ema_fast is None:
                ema_fast = analyzer.calculate_ema(self.config['moving_averages']['fast_period'])
            if ema_slow is None:
                ema_slow = analyzer.calculate_ema(self.config['moving_averages']['slow_period'])
            
            if len(ema_fast) > 1 and len(ema_slow) > 1:
                last_ema_fast = ema_fast.iloc[-1]
                last_ema_slow = ema_slow.iloc[-1]
                last_close = analyzer.df['close'].iloc[-1]
                
                indicators_used['EMA_Fast'] = round(last_ema_fast, 5)
                indicators_used['EMA_Slow'] = round(last_ema_slow, 5)
                
                # Tendencia alcista
                if last_ema_fast > last_ema_slow and last_close > last_ema_fast:
                    scores['buy'] += 1
                    reasons.append("Tendencia alcista en MAs")
                # Tendencia bajista
                elif last_ema_fast < last_ema_slow and last_close < last_ema_fast:
                    scores['sell'] += 1
                    reasons.append("Tendencia bajista en MAs")
        
        # ============ ATR (Volatilidad) ============
        if self.config['atr']['enabled']:
            atr = analyzer.indicators.get('ATR', None)
            if atr is not None:
                last_atr = atr.iloc[-1]
                last_close = analyzer.df['close'].iloc[-1]
                atr_percent = (last_atr / last_close) * 100
                
                indicators_used['ATR'] = round(last_atr, 5)
                indicators_used['ATR_%'] = round(atr_percent, 2)
        
        # ============ ADX (Tendencia) ============
        if self.config['adx']['enabled']:
            adx = analyzer.indicators.get('ADX', None)
            if adx is not None:
                last_adx = adx.iloc[-1]
                indicators_used['ADX'] = round(last_adx, 2)
                
                # Si hay tendencia fuerte, aumentar confianza
                if last_adx > self.config['adx']['strong_trend']:
                    # Aumentar score del lado de la tendencia
                    if scores['buy'] > scores['sell']:
                        scores['buy'] += 1
                    elif scores['sell'] > scores['buy']:
                        scores['sell'] += 1
        
        # ============ DECISIÓN FINAL ============
        
        # Calcular confianza
        total_score = scores['buy'] + scores['sell']
        if total_score == 0:
            confidence = 0
            signal_type = SignalType.HOLD
            strength = SignalStrength.WEAK
        else:
            confidence = max(scores['buy'], scores['sell']) / (total_score * 2)
            
            if scores['buy'] > scores['sell']:
                signal_type = SignalType.BUY
            elif scores['sell'] > scores['buy']:
                signal_type = SignalType.SELL
            else:
                signal_type = SignalType.HOLD
            
            # Determinar fortaleza
            diff = abs(scores['buy'] - scores['sell'])
            if diff >= 4:
                strength = SignalStrength.VERY_STRONG
            elif diff >= 3:
                strength = SignalStrength.STRONG
            elif diff >= 2:
                strength = SignalStrength.MEDIUM
            else:
                strength = SignalStrength.WEAK
        
        # Crear señal
        from datetime import datetime
        signal = Signal(
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasons=reasons if reasons else ["Sin indicadores concluyentes"],
            timestamp=datetime.now().isoformat(),
            indicators_used=indicators_used
        )
        
        self.signals_history.append(signal)
        return signal
    
    def print_signal(self, signal: Signal):
        """Imprime una señal de forma legible"""
        print("\n" + "="*60)
        print("SEÑAL GENERADA")
        print("="*60)
        print(f"Tipo:       {signal.signal_type.value}")
        print(f"Fortaleza:  {signal.strength.name}")
        print(f"Confianza:  {signal.confidence:.1%}")
        print(f"\nRazones:")
        for reason in signal.reasons:
            print(f"  • {reason}")
        print(f"\nIndicadores:")
        for name, value in signal.indicators_used.items():
            print(f"  {name}: {value}")
        print("="*60 + "\n")
    
    def export_config(self, filepath: str):
        """
        Exporta la configuración a un archivo JSON
        
        Args:
            filepath (str): Ruta del archivo
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✓ Configuración exportada a {filepath}")
        except Exception as e:
            logger.error(f"Error al exportar configuración: {str(e)}")
    
    def load_config(self, filepath: str):
        """
        Carga la configuración desde un archivo JSON
        
        Args:
            filepath (str): Ruta del archivo
        """
        try:
            with open(filepath, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✓ Configuración cargada desde {filepath}")
        except Exception as e:
            logger.error(f"Error al cargar configuración: {str(e)}")
