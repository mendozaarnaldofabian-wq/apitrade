"""
Motor de análisis de velas - Lectura y procesamiento de datos OHLC
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class CandleAnalyzer:
    """Analiza velas y calcula indicadores técnicos"""
    
    def __init__(self, df: pd.DataFrame = None):
        """
        Inicializa el analizador de velas
        
        Args:
            df (pd.DataFrame): DataFrame con datos OHLC
        """
        self.df = df if df is not None else pd.DataFrame()
        self.indicators = {}
    
    def load_candles_from_dict(self, candles: dict) -> bool:
        """
        Carga velas desde formato de diccionario (IQ Option)
        
        Args:
            candles (dict): Datos de velas de IQ Option
            
        Returns:
            bool: True si se cargaron correctamente
        """
        try:
            if not candles:
                logger.error("Sin datos de velas")
                return False
            
            # Convertir formato IQ Option a DataFrame
            data = {
                'time': [],
                'open': [],
                'high': [],
                'low': [],
                'close': [],
                'volume': []
            }
            
            # IQ Option retorna diccionario con timestamp como clave
            for timestamp, candle_data in sorted(candles.items()):
                data['time'].append(datetime.fromtimestamp(int(timestamp)))
                data['open'].append(candle_data.get('open', 0))
                data['high'].append(candle_data.get('max', 0))
                data['low'].append(candle_data.get('min', 0))
                data['close'].append(candle_data.get('close', 0))
                data['volume'].append(candle_data.get('volume', 0))
            
            self.df = pd.DataFrame(data)
            self.df.set_index('time', inplace=True)
            
            logger.info(f"✓ Cargadas {len(self.df)} velas")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar velas: {str(e)}")
            return False
    
    def load_candles_from_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Carga velas desde un DataFrame existente
        
        Args:
            df (pd.DataFrame): DataFrame con columnas OHLC
            
        Returns:
            bool: True si se cargaron correctamente
        """
        try:
            required_cols = ['open', 'high', 'low', 'close']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"DataFrame debe contener: {required_cols}")
                return False
            
            self.df = df.copy()
            logger.info(f"✓ Cargadas {len(self.df)} velas desde DataFrame")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar DataFrame: {str(e)}")
            return False
    
    # ============ INDICADORES BÁSICOS ============
    
    def calculate_sma(self, period: int = 20, column: str = 'close') -> pd.Series:
        """
        Calcula Media Móvil Simple (SMA)
        
        Args:
            period (int): Período en velas
            column (str): Columna a usar
            
        Returns:
            pd.Series: Valores de SMA
        """
        sma = self.df[column].rolling(window=period).mean()
        self.indicators[f'SMA_{period}'] = sma
        logger.debug(f"✓ SMA({period}) calculado")
        return sma
    
    def calculate_ema(self, period: int = 20, column: str = 'close') -> pd.Series:
        """
        Calcula Media Móvil Exponencial (EMA)
        
        Args:
            period (int): Período en velas
            column (str): Columna a usar
            
        Returns:
            pd.Series: Valores de EMA
        """
        ema = self.df[column].ewm(span=period, adjust=False).mean()
        self.indicators[f'EMA_{period}'] = ema
        logger.debug(f"✓ EMA({period}) calculado")
        return ema
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        Calcula Índice de Fuerza Relativa (RSI)
        Rango: 0-100 (>70 sobrecomprado, <30 sobrevendido)
        
        Args:
            period (int): Período en velas
            
        Returns:
            pd.Series: Valores de RSI
        """
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        self.indicators['RSI'] = rsi
        logger.debug(f"✓ RSI({period}) calculado")
        return rsi
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple:
        """
        Calcula MACD (Moving Average Convergence Divergence)
        
        Args:
            fast (int): Período EMA rápida
            slow (int): Período EMA lenta
            signal (int): Período de señal
            
        Returns:
            Tuple: (macd, signal_line, histogram)
        """
        ema_fast = self.df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['close'].ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        self.indicators['MACD'] = macd
        self.indicators['MACD_Signal'] = signal_line
        self.indicators['MACD_Histogram'] = histogram
        
        logger.debug(f"✓ MACD({fast},{slow},{signal}) calculado")
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Tuple:
        """
        Calcula Bandas de Bollinger
        
        Args:
            period (int): Período SMA
            std_dev (float): Desviaciones estándar
            
        Returns:
            Tuple: (upper_band, middle_band, lower_band)
        """
        middle_band = self.df['close'].rolling(window=period).mean()
        std = self.df['close'].rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        self.indicators['BB_Upper'] = upper_band
        self.indicators['BB_Middle'] = middle_band
        self.indicators['BB_Lower'] = lower_band
        
        logger.debug(f"✓ Bollinger Bands({period}) calculado")
        return upper_band, middle_band, lower_band
    
    def calculate_atr(self, period: int = 14) -> pd.Series:
        """
        Calcula Rango Verdadero Promedio (ATR)
        Mide volatilidad
        
        Args:
            period (int): Período en velas
            
        Returns:
            pd.Series: Valores de ATR
        """
        high_low = self.df['high'] - self.df['low']
        high_close = abs(self.df['high'] - self.df['close'].shift())
        low_close = abs(self.df['low'] - self.df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        self.indicators['ATR'] = atr
        logger.debug(f"✓ ATR({period}) calculado")
        return atr
    
    def calculate_adx(self, period: int = 14) -> pd.Series:
        """
        Calcula Índice Direccional Promedio (ADX)
        Mide tendencia (>25 tendencia fuerte)
        
        Args:
            period (int): Período en velas
            
        Returns:
            pd.Series: Valores de ADX
        """
        high_diff = self.df['high'].diff()
        low_diff = -self.df['low'].diff()
        
        pos_dm = pd.Series(0.0, index=self.df.index)
        neg_dm = pd.Series(0.0, index=self.df.index)
        
        pos_dm[high_diff > low_diff] = high_diff
        neg_dm[low_diff > high_diff] = low_diff
        
        atr = self.calculate_atr(period)
        pos_di = 100 * (pos_dm.rolling(period).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(period).mean() / atr)
        
        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(period).mean()
        
        self.indicators['ADX'] = adx
        logger.debug(f"✓ ADX({period}) calculado")
        return adx
    
    # ============ ANÁLISIS Y ESTADÍSTICAS ============
    
    def get_last_candle(self) -> Dict:
        """
        Obtiene datos de la última vela
        
        Returns:
            Dict: Datos de la última vela
        """
        if len(self.df) == 0:
            return None
        
        last = self.df.iloc[-1]
        return {
            'time': self.df.index[-1],
            'open': last['open'],
            'high': last['high'],
            'low': last['low'],
            'close': last['close'],
            'volume': last.get('volume', 0),
            'change': ((last['close'] - last['open']) / last['open'] * 100) if last['open'] != 0 else 0
        }
    
    def get_indicators(self) -> Dict:
        """
        Obtiene todos los indicadores calculados de la última vela
        
        Returns:
            Dict: Indicadores para la última vela
        """
        if len(self.df) == 0:
            return {}
        
        indicators_data = {}
        for indicator_name, indicator_series in self.indicators.items():
            last_value = indicator_series.iloc[-1]
            indicators_data[indicator_name] = last_value if not pd.isna(last_value) else None
        
        return indicators_data
    
    def print_summary(self):
        """Imprime un resumen del análisis"""
        print("\n" + "="*60)
        print("RESUMEN DE ANÁLISIS DE VELAS")
        print("="*60)
        
        last_candle = self.get_last_candle()
        if last_candle:
            print(f"\nÚltima vela (Tiempo: {last_candle['time']}):")
            print(f"  Open:   {last_candle['open']:.5f}")
            print(f"  High:   {last_candle['high']:.5f}")
            print(f"  Low:    {last_candle['low']:.5f}")
            print(f"  Close:  {last_candle['close']:.5f}")
            print(f"  Cambio: {last_candle['change']:+.2f}%")
        
        indicators = self.get_indicators()
        if indicators:
            print(f"\nIndicadores:")
            for name, value in indicators.items():
                if value is not None:
                    if isinstance(value, float):
                        print(f"  {name}: {value:.2f}")
                    else:
                        print(f"  {name}: {value}")
        
        print("="*60 + "\n")
