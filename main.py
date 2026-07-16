"""
Script principal del bot de trading
Integra: Conexión a IQ Option → Análisis de velas → Generación de señales
"""
import logging
import os
from dotenv import load_dotenv
import sys

# Importar módulos
from src.broker import IQOptionBroker
from src.candle_analyzer import CandleAnalyzer
from src.signal_generator import SignalGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


def test_broker_and_analysis():
    """
    Test completo: Conectar a IQ Option, obtener velas, analizar y generar señales
    """
    print("\n" + "="*70)
    print("PRUEBA COMPLETA: BROKER → ANÁLISIS → SEÑALES")
    print("="*70)
    
    # 1. INICIALIZAR BROKER
    print("\n[1/5] Inicializando conexión con IQ Option...")
    broker = IQOptionBroker(
        email=os.getenv('IQ_EMAIL'),
        password=os.getenv('IQ_PASSWORD'),
        is_demo=True
    )
    
    if not broker.connect():
        logger.error("✗ No se pudo conectar a IQ Option")
        return False
    
    # 2. OBTENER PERFIL
    print("[2/5] Obteniendo información de cuenta...")
    profile = broker.get_profile()
    if profile:
        balance = broker.get_balance()
        print(f"✓ Balance: ${balance:.2f}")
    
    # 3. OBTENER VELAS
    print("[3/5] Descargando velas históricas...")
    asset = os.getenv('IQ_CURRENCY_PAIR', 'EURUSD')
    timeframe = int(os.getenv('IQ_TIMEFRAME', 60))  # 60 segundos = 1 minuto
    
    candles = broker.get_candles(asset=asset, timeframe=timeframe, count=100)
    if not candles:
        logger.error("✗ No se pudieron obtener velas")
        broker.disconnect()
        return False
    
    # 4. ANALIZAR VELAS
    print("[4/5] Analizando velas e indicadores...")
    analyzer = CandleAnalyzer()
    analyzer.load_candles_from_dict(candles)
    
    # Calcular todos los indicadores
    analyzer.calculate_sma(20)
    analyzer.calculate_ema(20)
    analyzer.calculate_ema(50)
    analyzer.calculate_rsi(14)
    analyzer.calculate_macd()
    analyzer.calculate_bollinger_bands()
    analyzer.calculate_atr()
    analyzer.calculate_adx()
    
    # Mostrar resumen
    analyzer.print_summary()
    
    # 5. GENERAR SEÑALES
    print("[5/5] Generando señal de trading...")
    signal_gen = SignalGenerator()
    signal = signal_gen.generate_signal(analyzer)
    
    signal_gen.print_signal(signal)
    
    # Desconectar
    broker.disconnect()
    
    return True


def demo_with_sample_data():
    """
    Demo con datos de ejemplo (sin necesidad de conexión real a IQ Option)
    """
    print("\n" + "="*70)
    print("DEMO: ANÁLISIS Y SEÑALES CON DATOS DE EJEMPLO")
    print("="*70)
    
    import pandas as pd
    import numpy as np
    
    # Generar datos de ejemplo
    print("\n[1/4] Generando datos de ejemplo...")
    dates = pd.date_range(start='2024-06-01', periods=100, freq='h')
    
    # Generar precios realistas con tendencia alcista
    prices = np.random.randn(100).cumsum() + 100
    
    df = pd.DataFrame({
        'open': prices + np.random.randn(100) * 0.5,
        'high': prices + abs(np.random.randn(100)) * 1.5,
        'low': prices - abs(np.random.randn(100)) * 1.5,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # Crear analizador
    print("[2/4] Analizando indicadores...")
    analyzer = CandleAnalyzer()
    analyzer.load_candles_from_dataframe(df)
    
    # Calcular indicadores
    analyzer.calculate_sma(20)
    analyzer.calculate_ema(20)
    analyzer.calculate_ema(50)
    analyzer.calculate_rsi(14)
    analyzer.calculate_macd()
    analyzer.calculate_bollinger_bands()
    analyzer.calculate_atr()
    analyzer.calculate_adx()
    
    analyzer.print_summary()
    
    # Generar señal
    print("[3/4] Generando señal...")
    signal_gen = SignalGenerator()
    signal = signal_gen.generate_signal(analyzer)
    signal_gen.print_signal(signal)
    
    # Guardar configuración
    print("[4/4] Guardando configuración...")
    signal_gen.export_config('./config/signal_config.json')
    
    return True


def main():
    """Función principal"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           BOT DE TRADING - PROPUESTA 1 y 2                   ║")
    print("║                                                               ║")
    print("║  [1] Prueba real (conexión a IQ Option)                      ║")
    print("║  [2] Demo con datos de ejemplo                               ║")
    print("║  [3] Salir                                                    ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    choice = input("Selecciona una opción (1-3): ").strip()
    
    if choice == '1':
        print("\n⚠ ASEGÚRATE DE TENER CONFIGURADO:")
        print("  • .env con tus credenciales de IQ Option")
        print("  • Modo DEMO activado")
        input("\nPresiona Enter para continuar...")
        test_broker_and_analysis()
        
    elif choice == '2':
        demo_with_sample_data()
        
    elif choice == '3':
        print("✓ Hasta luego!")
        sys.exit(0)
    else:
        print("✗ Opción inválida")
        main()


if __name__ == "__main__":
    main()
