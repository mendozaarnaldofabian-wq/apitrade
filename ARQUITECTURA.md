# 🏗️ ARQUITECTURA DEL BOT DE TRADING

## Flujo General

```
┌─────────────────────────────────────────────────────────────────┐
│                   BOT DE TRADING - FLUJO COMPLETO                │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │   IQ OPTION      │
    │   (REAL/DEMO)    │
    └────────┬─────────┘
             │
             │ get_candles()
             │ (OHLC data)
             ▼
    ┌──────────────────────────────────────────────────┐
    │    1️⃣  BROKER (src/broker.py)                   │
    │                                                  │
    │  • connect() - Conexión con IQ Option           │
    │  • get_candles() - Obtener velas históricas     │
    │  • get_profile() - Info de cuenta               │
    │  • buy_call() / buy_put() - Operaciones (Prop5) │
    └────────────────┬─────────────────────────────────┘
                     │
                     │ Diccionario de velas
                     │ {timestamp: {open, high, low, close}}
                     ▼
    ┌──────────────────────────────────────────────────┐
    │    2️⃣  CANDLE ANALYZER (src/candle_analyzer.py) │  ← PROPUESTA 1
    │                                                  │
    │  • load_candles_from_dict()                      │
    │  • calculate_rsi()                               │
    │  • calculate_macd()                              │
    │  • calculate_bollinger_bands()                   │
    │  • calculate_ema() / calculate_sma()             │
    │  • calculate_atr()                               │
    │  • calculate_adx()                               │
    │                                                  │
    │  Output: DataFrame + Indicadores calculados      │
    └────────────────┬─────────────────────────────────┘
                     │
                     │ analyzer con indicators
                     ▼
    ┌──────────────────────────────────────────────────┐
    │   3️⃣  SIGNAL GENERATOR (src/signal_generator.py)│  ← PROPUESTA 2
    │                                                  │
    │  • generate_signal()                             │
    │    - Evalúa todas las reglas                     │
    │    - Combina indicadores                         │
    │    - Calcula confianza                           │
    │                                                  │
    │  Output: Signal {type, strength, confidence}     │
    └────────────────┬─────────────────────────────────┘
                     │
                     │ Signal (BUY/SELL/HOLD)
                     ▼
    ┌──────────────────────────────────────────────────┐
    │           DECISIÓN Y ACCIÓN                      │
    │                                                  │
    │  • Propuesta 3: BACKTESTING                      │
    │  • Propuesta 4: MODO DEMO                        │
    │  • Propuesta 5: AUTOMATIZACIÓN (buy/sell)        │
    └──────────────────────────────────────────────────┘
```

---

## Módulo 1️⃣: Broker (Conexión)

```python
IQOptionBroker
├── __init__(email, password, is_demo)
├── connect() → bool
│   ├── Autentica con IQ Option
│   ├── Establece modo DEMO o REAL
│   └── Retorna True/False
│
├── get_candles(asset, timeframe, count) → dict
│   ├── Solicita velas a IQ Option
│   │   asset: "EURUSD", "GBPUSD", etc
│   │   timeframe: 60, 300, 900, 3600 (segundos)
│   │   count: número de velas
│   └── Retorna: {timestamp: {open, high, low, close, volume}}
│
├── get_profile() → dict
│   └── Información de la cuenta
│
├── get_balance() → float
│   └── Balance actual
│
├── buy_call(asset, amount, duration) → dict  [Propuesta 5]
│   └── Abre operación CALL (precio sube)
│
└── buy_put(asset, amount, duration) → dict   [Propuesta 5]
    └── Abre operación PUT (precio baja)
```

---

## Módulo 2️⃣: CandleAnalyzer (Análisis - PROPUESTA 1)

```python
CandleAnalyzer
├── __init__(df=None)
│   └── Inicializa con DataFrame (opcional)
│
├── load_candles_from_dict(candles) → bool
│   └── Convierte datos IQ Option a DataFrame
│
├── load_candles_from_dataframe(df) → bool
│   └── Carga datos desde CSV/Excel
│
├── INDICADORES TÉCNICOS:
│   ├── calculate_rsi(period=14) → pd.Series
│   │   └── RSI = 100 - (100 / (1 + RS))
│   │   └── Rango: 0-100 (>70 sobrecomprado, <30 sobrevendido)
│   │
│   ├── calculate_macd(fast=12, slow=26, signal=9) → (macd, signal, histogram)
│   │   └── MACD = EMA12 - EMA26
│   │   └── Signal = EMA9(MACD)
│   │   └── Histogram = MACD - Signal
│   │
│   ├── calculate_bollinger_bands(period=20, std_dev=2.0) → (upper, middle, lower)
│   │   └── Middle = SMA20(close)
│   │   └── Upper = Middle + (STD * 2)
│   │   └── Lower = Middle - (STD * 2)
│   │
│   ├── calculate_ema(period=20, column='close') → pd.Series
│   │   └── EMA = precio * multiplicador + EMA_anterior * (1 - multiplicador)
│   │
│   ├── calculate_sma(period=20, column='close') → pd.Series
│   │   └── SMA = SUMA(últimas N velas) / N
│   │
│   ├── calculate_atr(period=14) → pd.Series
│   │   └── ATR = promedio del Rango Verdadero
│   │   └── Mide volatilidad en puntos
│   │
│   └── calculate_adx(period=14) → pd.Series
│       └── ADX = índice de fuerza de tendencia
│       └── Rango: 0-100 (>25 tendencia fuerte)
│
└── ANÁLISIS Y VISUALIZACIÓN:
    ├── get_last_candle() → dict
    │   └── Datos de la última vela
    │
    ├── get_indicators() → dict
    │   └── Todos los indicadores de la última vela
    │
    └── print_summary()
        └── Imprime análisis formateado
```

---

## Módulo 3️⃣: SignalGenerator (Generador de Señales - PROPUESTA 2)

```python
SignalGenerator
├── __init__(config=None)
│   └── Inicializa con configuración (default o personalizada)
│
├── CONFIGURACIÓN:
│   ├── get_default_config() → dict
│   │   ├── rsi: {enabled, overbought, oversold, period}
│   │   ├── macd: {enabled, fast, slow, signal}
│   │   ├── bollinger: {enabled, period, std_dev}
│   │   ├── moving_averages: {enabled, fast_period, slow_period}
│   │   ├── atr: {enabled, period}
│   │   ├── adx: {enabled, period, strong_trend}
│   │   └── min_confidence: 0.5
│   │
│   ├── update_config(new_config) → None
│   │   └── Actualiza configuración
│   │
│   ├── load_config(filepath) → None
│   │   └── Carga desde JSON
│   │
│   └── export_config(filepath) → None
│       └── Guarda a JSON
│
├── GENERACIÓN DE SEÑALES:
│   └── generate_signal(analyzer) → Signal
│       │
│       ├── Paso 1: Evaluar RSI
│       │   ├── Si RSI < 30 → score['buy'] += 2
│       │   └── Si RSI > 70 → score['sell'] += 2
│       │
│       ├── Paso 2: Evaluar MACD
│       │   ├── Si MACD cruza arriba signal → score['buy'] += 2
│       │   └── Si MACD cruza abajo signal → score['sell'] += 2
│       │
│       ├── Paso 3: Evaluar Bollinger Bands
│       │   ├── Si precio < banda_baja → score['buy'] += 1
│       │   └── Si precio > banda_alta → score['sell'] += 1
│       │
│       ├── Paso 4: Evaluar Moving Averages
│       │   ├── Si EMA_rápida > EMA_lenta y precio > EMA → score['buy'] += 1
│       │   └── Si EMA_rápida < EMA_lenta y precio < EMA → score['sell'] += 1
│       │
│       ├── Paso 5: Evaluar ADX
│       │   ├── Si ADX > 25 y buy_score > sell_score → buy_score += 1
│       │   └── Si ADX > 25 y sell_score > buy_score → sell_score += 1
│       │
│       └── Paso 6: Decisión Final
│           ├── Calcular confianza = max(buy, sell) / (buy + sell) / 2
│           ├── Si buy > sell → BUY
│           ├── Si sell > buy → SELL
│           └── Si buy = sell → HOLD
│
└── SALIDA:
    └── Signal {
        type: SignalType (BUY/SELL/HOLD),
        strength: SignalStrength (WEAK/MEDIUM/STRONG/VERY_STRONG),
        confidence: float (0-1),
        reasons: [str],
        timestamp: str,
        indicators_used: dict
    }
```

---

## Flujo de Confianza y Fortaleza

```
Scores (buy vs sell):
    ├── Diferencia 4+ puntos → VERY_STRONG (confianza: 75-100%)
    ├── Diferencia 3 puntos  → STRONG (confianza: 60-75%)
    ├── Diferencia 2 puntos  → MEDIUM (confianza: 40-60%)
    └── Diferencia 1 punto   → WEAK (confianza: 20-40%)

Ejemplo:
    buy_score = 4  (RSI + MACD + Bollinger + MA)
    sell_score = 0
    diferencia = 4
    → Fortaleza: VERY_STRONG
    → Confianza: 80%
    → Señal: BUY
```

---

## Flujo Completo: Ejemplo

```
INPUT: Par EURUSD, 100 velas de 1 minuto

1. BROKER
   broker.get_candles('EURUSD', 60, 100)
   └─→ {timestamp1: {open, high, low, close},
        timestamp2: {open, high, low, close}, ...}

2. CANDLE ANALYZER
   analyzer.load_candles_from_dict(candles)
   analyzer.calculate_rsi()
   analyzer.calculate_macd()
   analyzer.calculate_bollinger_bands()
   analyzer.calculate_ema(20)
   analyzer.calculate_ema(50)
   analyzer.calculate_atr()
   analyzer.calculate_adx()
   
   ├─ DataFrame: 100 filas × 6 columnas (OHLCV)
   └─ Indicadores calculados para cada vela

3. SIGNAL GENERATOR
   signal_gen.generate_signal(analyzer)
   
   ├─ RSI(14) = 65.4 → score['sell'] += 2 (sobrecomprado)
   ├─ MACD cruce = negativo → score['sell'] += 2
   ├─ Bollinger = cerca banda alta → score['sell'] += 1
   ├─ EMA_20 > EMA_50 pero precio < EMA_20 → neutral
   └─ ADX = 28 (tendencia fuerte) → sell_score += 1
   
   Total: buy_score=0, sell_score=6
   → Señal: SELL, Fortaleza: VERY_STRONG, Confianza: 100%

OUTPUT: 
   {
     type: "SELL",
     strength: "VERY_STRONG",
     confidence: "100%",
     reasons: [
       "RSI sobrecomprado (65.4)",
       "MACD cruce bajista",
       "Precio sobre banda superior",
       "Tendencia fuerte"
     ]
   }
```

---

## Archivos de Configuración

### `signal_config.json` (Exportable/Importable)

```json
{
  "rsi": {
    "enabled": true,
    "overbought": 70,
    "oversold": 30,
    "period": 14
  },
  "macd": {
    "enabled": true,
    "fast": 12,
    "slow": 26,
    "signal": 9
  },
  "bollinger": {
    "enabled": true,
    "period": 20,
    "std_dev": 2.0
  },
  "moving_averages": {
    "enabled": true,
    "fast_period": 20,
    "slow_period": 50
  },
  "atr": {
    "enabled": true,
    "period": 14
  },
  "adx": {
    "enabled": true,
    "period": 14,
    "strong_trend": 25
  },
  "min_confidence": 0.5
}
```

---

## Propuestas Futuras (3, 4, 5)

```
┌─────────────────────────────────────────────────────────┐
│  PROPUESTA 3: BACKTESTING                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Histórico CSV → Analyzer → Signal Generator            │
│           ↓                                              │
│  Ejecutar todas las señales en datos históricos         │
│           ↓                                              │
│  Métricas: ROI, Drawdown, Win Rate, Ratio              │
│           ↓                                              │
│  Optimización: Ajustar parámetros de indicadores       │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PROPUESTA 4: MODO DEMO                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tiempo Real → Analyzer → Signal Generator              │
│           ↓                                              │
│  Ejecutar señales como si fueran reales (simulado)      │
│           ↓                                              │
│  Registrar: entrada, salida, ganancias/pérdidas        │
│           ↓                                              │
│  Dashboard: Ver histórico de operaciones               │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PROPUESTA 5: AUTOMATIZACIÓN                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tiempo Real → Analyzer → Signal Generator              │
│           ↓                                              │
│  Si Signal = BUY → broker.buy_call()                   │
│  Si Signal = SELL → broker.buy_put()                   │
│           ↓                                              │
│  Gestión: Stop Loss, Take Profit, Money Management     │
│           ↓                                              │
│  Logging: Histórico en base de datos                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

```
Python 3.8+
│
├── IQ Option API
│   └── iqoptionapi (conexión)
│
├── Data Processing
│   ├── pandas (DataFrames)
│   ├── numpy (cálculos numéricos)
│   └── ta (indicadores técnicos)
│
├── Backtesting (Propuesta 3)
│   └── backtesting.py
│
└── Storage
    ├── SQLite (histórico)
    └── JSON (configuración)
```

---

## Conclusión

**Propuestas 1 y 2** proporcionan la base sólida para:
- **Análisis técnico** robusto
- **Generación de señales** flexible y configurable
- **Testing** sin necesidad de dinero real

**Propuestas 3-5** escalarán el sistema a:
- Backtesting y optimización
- Validación en tiempo real
- Operaciones completamente automatizadas

🚀 **¡Listo para programar!**
