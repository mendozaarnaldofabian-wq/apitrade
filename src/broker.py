"""
Módulo para gestionar la conexión con IQ Option API
"""
import logging
from iqoptionapi.stable_api import IQ_Option
import time

logger = logging.getLogger(__name__)


class IQOptionBroker:
    """Gestor de conexión y operaciones con IQ Option"""
    
    def __init__(self, email: str, password: str, is_demo: bool = True):
        """
        Inicializa la conexión con IQ Option
        
        Args:
            email (str): Email de IQ Option
            password (str): Contraseña de IQ Option
            is_demo (bool): True para modo demo, False para live
        """
        self.email = email
        self.password = password
        self.is_demo = is_demo
        self.api = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Establece conexión con IQ Option
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            logger.info(f"Conectando a IQ Option como {self.email}...")
            self.api = IQ_Option(self.email, self.password)
            
            # Esperar a que se complete la conexión
            check_connect = self.api.check_connect()
            
            if not check_connect:
                logger.error("No se pudo conectar a IQ Option")
                return False
            
            logger.info("✓ Conectado a IQ Option exitosamente")
            
            # Establecer modo demo o live
            if self.is_demo:
                self.api.change_balance("DEMO")
                logger.info("✓ Modo DEMO activo")
            else:
                self.api.change_balance("REAL")
                logger.warning("⚠ Modo REAL activo - Cuidado con operaciones reales")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Error al conectar: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta de IQ Option"""
        if self.api:
            try:
                self.api.logout()
                logger.info("✓ Desconectado de IQ Option")
            except Exception as e:
                logger.error(f"Error al desconectar: {str(e)}")
        self.connected = False
    
    def get_candles(self, asset: str, timeframe: int, count: int = 100) -> dict:
        """
        Obtiene velas históricas
        
        Args:
            asset (str): Par de divisas (ej: EURUSD)
            timeframe (int): Período en segundos (60, 300, 900, 3600)
            count (int): Cantidad de velas a obtener
            
        Returns:
            dict: Datos de las velas
        """
        try:
            if not self.connected:
                logger.error("No conectado a IQ Option")
                return None
            
            # Obtener las velas
            logger.debug(f"Obteniendo {count} velas de {asset} (timeframe: {timeframe}s)")
            candles = self.api.get_candles(asset, timeframe, count)
            
            if candles:
                logger.debug(f"✓ Obtenidas {len(candles)} velas")
                return candles
            else:
                logger.warning(f"No se obtuvieron velas para {asset}")
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener velas: {str(e)}")
            return None
    
    def get_profile(self) -> dict:
        """
        Obtiene información del perfil
        
        Returns:
            dict: Información de la cuenta
        """
        try:
            profile = self.api.get_profile()
            return profile
        except Exception as e:
            logger.error(f"Error al obtener perfil: {str(e)}")
            return None
    
    def get_balance(self) -> float:
        """
        Obtiene el balance actual
        
        Returns:
            float: Balance en cuenta
        """
        try:
            profile = self.get_profile()
            if profile:
                return profile.get('balance', 0)
            return 0
        except Exception as e:
            logger.error(f"Error al obtener balance: {str(e)}")
            return 0
    
    def buy_call(self, asset: str, amount: float, duration: int) -> dict:
        """
        Abre una operación CALL (precio sube)
        
        Args:
            asset (str): Par de divisas
            amount (float): Monto a invertir
            duration (int): Duración en segundos
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            result = self.api.buy(amount, asset, "call", duration)
            return result
        except Exception as e:
            logger.error(f"Error al abrir CALL: {str(e)}")
            return None
    
    def buy_put(self, asset: str, amount: float, duration: int) -> dict:
        """
        Abre una operación PUT (precio baja)
        
        Args:
            asset (str): Par de divisas
            amount (float): Monto a invertir
            duration (int): Duración en segundos
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            result = self.api.buy(amount, asset, "put", duration)
            return result
        except Exception as e:
            logger.error(f"Error al abrir PUT: {str(e)}")
            return None
    
    def check_live_deal(self, deal_id: str) -> dict:
        """
        Verifica el estado de una operación abierta
        
        Args:
            deal_id (str): ID de la operación
            
        Returns:
            dict: Estado de la operación
        """
        try:
            status = self.api.check_win_v4(deal_id)
            return status
        except Exception as e:
            logger.error(f"Error al verificar operación: {str(e)}")
            return None
