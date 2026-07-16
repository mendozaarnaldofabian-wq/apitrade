# 🚀 BOT DE TRADING - GUÍA RÁPIDA DE INICIO

**Propuestas 1 y 2 completamente implementadas y listas para usar**

---

## 📦 ¿Qué hemos creado?

### **Propuesta 1: Motor de Análisis de Velas** ✅
- Lee datos OHLC en tiempo real de IQ Option
- Calcula 7 indicadores técnicos principales
- Proporciona análisis estadístico detallado
- **Archivo principal**: `src/candle_analyzer.py`

### **Propuesta 2: Generador de Señales** ✅
- Reglas claras y configurables
- Combina múltiples indicadores
- Genera señales: BUY / SELL / HOLD
- Asigna fuerza y confianza
- **Archivo principal**: `src/signal_generator.py`

---

## 📁 Estructura Completa

```
trading-bot/
├── src/
│   ├── __init__.py                 # Paquete Python
│   ├── broker.py                   # Conexión IQ Option
│   ├── candle_analyzer.py          # Motor de análisis ← PROPUESTA 1
│   └── signal_generator.py         # Generador de señales ← PROPUESTA 2
├── config/
│   └── signal_config.json          # Configuración exportable
├── main.py                          # Script principal (menú interactivo)
├── test_signals.py                  # Tests sin necesidad de IQ Option
├── requirements.txt                 # Dependencias
├── .env.example                     # Variables de entorno
└── README.md                        # Documentación completa
```

---

## ⚡ 3 Pasos para Empezar

### **PASO 1: Instalar**
```bash
cd trading-bot
pip install -r requirements.txt
```

### **PASO 2: Configurar**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# IQ_EMAIL=tu_email@iq-option.com
# IQ_PASSWORD=tu_contraseña
```

### **PASO 3: Ejecutar**
```bash
# Opción A: Con prueba real (requiere credenciales)
python main.py
# Selecciona opción 1

# Opción B: Demo con datos de ejemplo (NO requiere credenciales)
python main.py
# Selecciona opción 2

# Opción C: Ejecutar tests
python test_signals.py
```

---

## 📊 ¿Qué Verás?

### **Output del Análisis:**
```
============================================================
RESUMEN DE ANÁLISIS DE VELAS
============================================================

Última vela (Tiempo: 2024-07-11 15:30:00):
  Open:   1.07350
  High:   1.07420
  Low:    1.07280
  Close:  1.07390
  Cambio: +0.06%

Indicadores:
  SMA_20: 1.07256
  EMA_20: 1.07345
  RSI: 65.42
  MACD: 0.00145
  BB_Upper: 1.07512
  BB_Lower: 1.07045
  ATR: 0.00067
  ADX: 32.15
```

### **Output de la Señal:**
```
============================================================
SEÑAL GENERADA
============================================================
Tipo:       BUY
Fortaleza:  STRONG
Confianza:  75%

Razones:
  • RSI sobrevendido (28.5)
  • MACD cruce alcista
  • Tendencia alcista en MAs

Indicadores Usados:
  RSI: 28.5
  MACD: 0.00145
  EMA_Fast: 1.07345
  EMA_Slow: 1.07210
```

---

## 🎯 Indicadores Implementados

| Indicador | Rango | Qué Detecta | En Código |
|-----------|-------|------------|----------|
| **RSI** | 0-100 | Sobrecompra/Sobreventa | `calculate_rsi()` |
| **MACD** | -∞ a +∞ | Momentum y cruces | `calculate_macd()` |
| **Bollinger Bands** | Precio | Volatilidad y rebotes | `calculate_bollinger_bands()` |
| **EMA** | Precio | Tendencia exponencial | `calculate_ema()` |
| **SMA** | Precio | Tendencia simple | `calculate_sma()` |
| **ATR** | +∞ | Volatilidad (en puntos) | `calculate_atr()` |
| **ADX** | 0-100 | Fuerza de tendencia | `calculate_adx()` |

---

## 🔧 Configuración Personalizada

### **Opción 1: Cambiar en código**
```python
from src.signal_generator import SignalGenerator

# Configuración personalizada
config = SignalGenerator.get_default_config()
config['rsi']['overbought'] = 75  # Cambiar umbral
config['rsi']['oversold'] = 25

signal_gen = SignalGenerator(config)
```

### **Opción 2: Usar archivo JSON**
```python
signal_gen = SignalGenerator()
signal_gen.load_config('./config/signal_config.json')
signal_gen.export_config('./config/mi_config.json')
```

### **Opción 3: Cambiar variables de entorno**
```
IQ_CURRENCY_PAIR=GBPUSD  # Cambiar par (EURUSD, GBPUSD, etc)
IQ_TIMEFRAME=300         # Cambiar timeframe (60, 300, 900, 3600)
```

---

## 💻 Ejemplos Prácticos

### **Ejemplo 1: Obtener velas y analizar**
```python
from src.broker import IQOptionBroker
from src.candle_analyzer import CandleAnalyzer

# Conectar
broker = IQOptionBroker("email@example.com", "password")
broker.connect()

# Obtener velas (últimas 100 de 1 minuto)
candles = broker.get_candles('EURUSD', 60, 100)

# Analizar
analyzer = CandleAnalyzer()
analyzer.load_candles_from_dict(candles)
analyzer.calculate_rsi()
analyzer.calculate_macd()

# Ver resultados
last_candle = analyzer.get_last_candle()
indicators = analyzer.get_indicators()
print(f"Precio actual: {last_candle['close']}")
print(f"RSI: {indicators['RSI']}")
```

### **Ejemplo 2: Generar señal con reglas personalizadas**
```python
from src.signal_generator import SignalGenerator

# Config personalizada
config = SignalGenerator.get_default_config()
config['rsi']['overbought'] = 80  # Más restrictivo

signal_gen = SignalGenerator(config)
signal = signal_gen.generate_signal(analyzer)

print(f"Señal: {signal.signal_type.value}")
print(f"Confianza: {signal.confidence:.1%}")
print(f"Razones: {signal.reasons}")
```

### **Ejemplo 3: Usar datos históricos**
```python
import pandas as pd
from src.candle_analyzer import CandleAnalyzer

# Cargar datos de CSV
df = pd.read_csv('eurusd_historical.csv', index_col='timestamp')

# Analizar
analyzer = CandleAnalyzer()
analyzer.load_candles_from_dataframe(df)
analyzer.calculate_sma(20)
analyzer.calculate_rsi(14)

analyzer.print_summary()
```

---

## 🧪 Testing Sin Conexión Real

**Perfecto para debugging:**
```bash
python test_signals.py
```

Ejecuta 4 tests automáticos:
1. ✓ Detección de tendencia alcista
2. ✓ Detección de tendencia bajista  
3. ✓ Detección de consolidación
4. ✓ Detección de extremos RSI

---

## 📚 Archivos Clave Explicados

### `src/broker.py`
**Responsabilidad**: Conexión con IQ Option API
- `connect()` - Conectar a IQ Option
- `get_candles()` - Obtener velas históricas
- `get_balance()` - Verificar balance
- `buy_call()` / `buy_put()` - Abrir operaciones (para Propuesta 5)

### `src/candle_analyzer.py`
**Responsabilidad**: Análisis técnico (PROPUESTA 1)
- `calculate_rsi()` - Índice de Fuerza Relativa
- `calculate_macd()` - MACD
- `calculate_bollinger_bands()` - Bandas de Bollinger
- `calculate_ema()` / `calculate_sma()` - Medias móviles
- `calculate_atr()` - Rango Verdadero Promedio
- `calculate_adx()` - Índice Direccional
- `print_summary()` - Ver análisis completo

### `src/signal_generator.py`
**Responsabilidad**: Generar señales (PROPUESTA 2)
- `generate_signal()` - Genera BUY/SELL/HOLD basado en reglas
- `update_config()` - Personalizar reglas
- `export_config()` / `load_config()` - Guardar/cargar configuración

---

## 🚀 Próximos Pasos (Propuestas 3-5)

**Ya están diseñadas**, solo necesitan implementación:

### **Propuesta 3: Backtesting**
- Probar estrategia en datos históricos
- Calcular métricas: ROI, drawdown, ratio ganancias/pérdidas
- Optimizar parámetros

### **Propuesta 4: Modo Demo**
- Validar señales en tiempo real
- Registrar operaciones simuladas
- Medir rendimiento sin riesgo

### **Propuesta 5: Automatización**
- Ejecutar CALL/PUT automáticamente
- Gestionar stop-loss y take-profit
- Registrar operaciones en base de datos

---

## ⚠️ Notas Importantes

✓ **Para Testing**: Usa opción 2 (demo) sin credenciales
✓ **Para Desarrollo**: Ejecuta `test_signals.py`
✓ **Para Real**: Asegúrate de modo DEMO primero

⚠️ **Disclaimer**:
- Este es un proyecto educativo
- No garantiza ganancias
- Trading conlleva riesgo
- Responsabilidad: tuya

---

## 🆘 Troubleshooting

| Problema | Solución |
|----------|----------|
| "No se pudo conectar" | Verifica .env con credenciales correctas |
| "Sin datos de velas" | Aumenta `count=100` en `get_candles()` |
| "Señal siempre HOLD" | Aumenta período a 100+ velas |
| "Error de import" | Ejecuta `pip install -r requirements.txt` |

---

## 📖 Documentación Completa

Ver `README.md` para:
- Instalación detallada
- Configuración avanzada
- Algoritmos de indicadores
- Referencias y recursos

---

## 🎯 Estado Actual

**Completado:**
- ✅ Propuesta 1: Motor de análisis (7 indicadores)
- ✅ Propuesta 2: Generador de señales (reglas configurables)

**Next Step:**
- Propuesta 3: Backtesting
- Propuesta 4: Modo demo
- Propuesta 5: Automatización

---

**¿Listo para empezar?**

```bash
cd trading-bot
python main.py
```

🚀 ¡Adelante!
