"""
GCM Heikin Ashi RSI Trend Cloud (GCM HRTC) Indicator
Adaptado do código Pine Script para Python
"""
import pandas as pd
import numpy as np


class GCMIndicator:
    """Implementa o indicador GCM Heikin Ashi RSI Trend Cloud"""
    
    def __init__(self, 
                 len_harsi: int = 10,
                 smoothing: int = 5,
                 len_rsi: int = 7,
                 upper: float = 20.0,
                 lower: float = -20.0,
                 upper_extreme: float = 30.0,
                 lower_extreme: float = -30.0):
        """
        Inicializa o indicador GCM HRT
        
        Args:
            len_harsi: Comprimento para cálculo do Heikin Ashi RSI
            smoothing: Suavização da abertura
            len_rsi: Comprimento para cálculo do RSI
            upper: Nível de sobrecompra (OB)
            lower: Nível de sobrevenda (OS)
            upper_extreme: Nível de sobrecompra extrema
            lower_extreme: Nível de sobrevenda extrema
        """
        self.len_harsi = len_harsi
        self.smoothing = smoothing
        self.len_rsi = len_rsi
        self.upper = upper
        self.lower = lower
        self.upper_extreme = upper_extreme
        self.lower_extreme = lower_extreme
    
    def calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        """Calcula o RSI (Relative Strength Index)"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_zrsi(self, series: pd.Series, period: int) -> pd.Series:
        """Calcula o Zero-centered RSI (RSI - 50)"""
        rsi = self.calculate_rsi(series, period)
        return rsi - 50
    
    def calculate_smoothed_rsi(self, df: pd.DataFrame, source_col: str = 'close') -> pd.Series:
        """Calcula o RSI suavizado (modo smoothed)"""
        zrsi = self.calculate_zrsi(df[source_col], self.len_rsi)
        
        # Suavização
        smoothed = pd.Series(index=df.index, dtype=float)
        for i in range(len(df)):
            if i == 0 or pd.isna(smoothed.iloc[i-1]):
                smoothed.iloc[i] = zrsi.iloc[i]
            else:
                smoothed.iloc[i] = (smoothed.iloc[i-1] + zrsi.iloc[i]) / 2
        
        return smoothed
    
    def calculate_heikin_ashi_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o Heikin Ashi RSI
        
        Returns:
            DataFrame com colunas: ha_open, ha_high, ha_low, ha_close
        """
        # Calcula RSI para cada preço
        close_rsi = self.calculate_zrsi(df['close'], self.len_harsi)
        high_rsi_raw = self.calculate_zrsi(df['high'], self.len_harsi)
        low_rsi_raw = self.calculate_zrsi(df['low'], self.len_harsi)
        
        # Ajusta high e low
        high_rsi = pd.Series([max(h, l) for h, l in zip(high_rsi_raw, low_rsi_raw)], index=df.index)
        low_rsi = pd.Series([min(h, l) for h, l in zip(high_rsi_raw, low_rsi_raw)], index=df.index)
        
        # Calcula Heikin Ashi
        ha_close = (close_rsi + high_rsi + low_rsi + close_rsi.shift(1).fillna(close_rsi)) / 4
        
        # Calcula abertura suavizada
        ha_open = pd.Series(index=df.index, dtype=float)
        for i in range(len(df)):
            if i < self.smoothing or pd.isna(ha_open.iloc[i-self.smoothing]):
                ha_open.iloc[i] = (close_rsi.iloc[i] + close_rsi.shift(1).fillna(close_rsi).iloc[i]) / 2
            else:
                ha_open.iloc[i] = (ha_open.iloc[i-1] * self.smoothing + ha_close.iloc[i-1]) / (self.smoothing + 1)
        
        # Calcula high e low finais
        ha_high = pd.Series([max(h, o, c) for h, o, c in zip(high_rsi, ha_open, ha_close)], index=df.index)
        ha_low = pd.Series([min(l, o, c) for l, o, c in zip(low_rsi, ha_open, ha_close)], index=df.index)
        
        return pd.DataFrame({
            'ha_open': ha_open,
            'ha_high': ha_high,
            'ha_low': ha_low,
            'ha_close': ha_close
        })
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos os indicadores
        
        Args:
            df: DataFrame com colunas OHLCV (open, high, low, close, volume)
            
        Returns:
            DataFrame com todos os indicadores calculados
        """
        result = df.copy()
        
        # Calcula o RSI suavizado
        result['rsi'] = self.calculate_smoothed_rsi(df)
        
        # Calcula o Heikin Ashi RSI
        ha_rsi = self.calculate_heikin_ashi_rsi(df)
        result = pd.concat([result, ha_rsi], axis=1)
        
        # Identifica tendência
        result['rsi_rising'] = result['rsi'] >= result['rsi'].shift(1)
        result['ha_bullish'] = result['ha_close'] > result['ha_open']
        
        # Sinais de cruzamento
        result['cross_upper'] = (result['rsi'] > self.upper) & (result['rsi'].shift(1) <= self.upper)
        result['cross_lower'] = (result['rsi'] < self.lower) & (result['rsi'].shift(1) >= self.lower)
        
        # Sinais de cruzamento extremo
        result['cross_upper_extreme'] = (result['rsi'] > self.upper_extreme) & (result['rsi'].shift(1) <= self.upper_extreme)
        result['cross_lower_extreme'] = (result['rsi'] < self.lower_extreme) & (result['rsi'].shift(1) >= self.lower_extreme)
        
        # Sinais de reversão (baseado no HARSI)
        result['harsi_bull'] = (result['ha_close'] > result['ha_open']) & ~(result['ha_close'].shift(1) > result['ha_open'].shift(1)).fillna(False)
        result['harsi_bear'] = (result['ha_close'] < result['ha_open']) & ~(result['ha_close'].shift(1) < result['ha_open'].shift(1)).fillna(False)
        
        # Sinais de reversão (baseado no RSI)
        result['rsi_bull'] = result['rsi_rising'].fillna(False) & ~result['rsi_rising'].shift(1).fillna(True)
        result['rsi_bear'] = ~result['rsi_rising'].fillna(True) & result['rsi_rising'].shift(1).fillna(False)
        
        # Sinais confirmados nas zonas críticas
        # COMPRA: RSI em sobrevenda (-20) + reversão bullish (bolinha verde)
        result['confirmed_buy'] = (result['rsi'] <= self.lower) & result['rsi_bull']
        
        # VENDA: RSI em sobrecompra (+20) + reversão bearish (bolinha vermelha)
        result['confirmed_sell'] = (result['rsi'] >= self.upper) & result['rsi_bear']
        
        return result
    
    def get_signal(self, df: pd.DataFrame) -> dict:
        """
        Retorna o sinal atual baseado nos últimos dados
        
        Returns:
            dict com informações do sinal
        """
        if len(df) == 0:
            return {'signal': 'NONE', 'strength': 0, 'message': 'Sem dados'}
        
        last_row = df.iloc[-1]
        
        signal_type = 'NONE'
        strength = 0
        message = ''
        rsi_value = float(last_row['rsi'])
        
        # PRIORIDADE 1: Sinais confirmados nas zonas críticas (+20/-20)
        if last_row['confirmed_buy']:
            signal_type = 'BUY'
            strength = 3
            message = f'🟢 COMPRA: RSI em {rsi_value:.1f} (sobrevenda) + reversão bullish (bolinha verde)'
        elif last_row['confirmed_sell']:
            signal_type = 'SELL'
            strength = 3
            message = f'🔴 VENDA: RSI em {rsi_value:.1f} (sobrecompra) + reversão bearish (bolinha vermelha)'
        
        # PRIORIDADE 2: Cruzamentos extremos
        elif last_row['cross_lower_extreme']:
            signal_type = 'BUY'
            strength = 2
            message = f'RSI cruzou {self.lower_extreme} (sobrevenda extrema)'
        elif last_row['cross_upper_extreme']:
            signal_type = 'SELL'
            strength = 2
            message = f'RSI cruzou {self.upper_extreme} (sobrecompra extrema)'
        
        # PRIORIDADE 3: Alertas de zona (sem reversão ainda)
        elif last_row['cross_lower']:
            signal_type = 'BUY'
            strength = 1
            message = f'⚠️ Alerta: RSI cruzou {self.lower} (aguardando reversão)'
        elif last_row['cross_upper']:
            signal_type = 'SELL'
            strength = 1
            message = f'⚠️ Alerta: RSI cruzou {self.upper} (aguardando reversão)'
        
        # PRIORIDADE 4: Reversões fora das zonas
        elif last_row['rsi_bull'] and rsi_value > self.lower:
            signal_type = 'BUY'
            strength = 1
            message = f'Reversão bullish no RSI (fora da zona de sobrevenda)'
        elif last_row['rsi_bear'] and rsi_value < self.upper:
            signal_type = 'SELL'
            strength = 1
            message = f'Reversão bearish no RSI (fora da zona de sobrecompra)'
        
        return {
            'signal': signal_type,
            'strength': strength,
            'message': message,
            'rsi': float(last_row['rsi']),
            'ha_open': float(last_row['ha_open']),
            'ha_close': float(last_row['ha_close']),
            'ha_bullish': bool(last_row['ha_bullish']),
            'price': float(last_row['close'])
        }
