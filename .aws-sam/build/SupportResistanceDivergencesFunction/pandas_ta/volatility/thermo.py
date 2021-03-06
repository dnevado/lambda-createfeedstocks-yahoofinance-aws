# -*- coding: utf-8 -*-
import numpy as np
from pandas import DataFrame, Series
from pandas_ta.overlap import ema, sma
from pandas_ta.utils import get_offset, verify_series, get_drift


def thermo(high, low, length=None, long=None, short=None, mamode=None, drift=None, offset=None, **kwargs):
    """Indicator: Elders Thermometer (THERMO)"""
    # Validate arguments
    high = verify_series(high)
    low = verify_series(low)
    drift = get_drift(drift)
    offset = get_offset(offset)
    length = int(length) if length and length > 0 else 20
    long = float(long) if long and long > 0 else 2
    short = float(short) if short and short > 0 else 0.5
    mamode = mamode.lower() if mamode else "ema"
    asint = kwargs.pop("asint", True)

    # Calculate Result
    thermoL = (low.shift(drift) - low).abs()
    thermoH = (high - high.shift(drift)).abs()

    thermo = thermoL
    thermo = thermo.where(thermoH < thermoL, thermoH)
    thermo.index = high.index

    if mamode == "sma":
        thermo_ma = sma(thermo, length)
    if mamode == "hma":
        thermo_ma = hma(thermo, length)
    else: # "ema"
        thermo_ma = ema(thermo, length)

    # Create signals
    thermo_long = thermo < (thermo_ma * long)
    thermo_short = thermo > (thermo_ma * short)

    # Binary output, useful for signals
    if asint:
        thermo_long = thermo_long.astype(int)  
        thermo_short = thermo_short.astype(int)

    # Offset
    if offset != 0:
        thermo = thermo.shift(offset)
        thermo_ma = thermo_ma.shift(offset)
        therthermo_longmo_ma = thermo_ma.shift(offset)
        thermo_short = thermo_ma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        thermo.fillna(kwargs["fillna"], inplace=True)
        thermo_ma.fillna(kwargs["fillna"], inplace=True)
        thermo_long.fillna(kwargs["fillna"], inplace=True)
        thermo_short.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        thermo.fillna(method=kwargs["fill_method"], inplace=True)
        thermo_ma.fillna(method=kwargs["fill_method"], inplace=True)
        thermo_long.fillna(method=kwargs["fill_method"], inplace=True)
        thermo_short.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    _props = f"_{length}_{long}_{short}"
    thermo.name = f"THERMO{_props}"
    thermo_ma.name = f"THERMOma{_props}"
    thermo_long.name = f"THERMOl{_props}"
    thermo_short.name = f"THERMOs{_props}"
    
    thermo.category = thermo_ma.category = thermo_long.category = thermo_short.category = "volatility"

    # Prepare Dataframe to return
    data = {thermo.name: thermo, thermo_ma.name: thermo_ma, thermo_long.name: thermo_long, thermo_short.name: thermo_short}
    df = DataFrame(data)
    df.name = f"THERMO{_props}"
    df.category = thermo.category

    return df



thermo.__doc__ = \
"""Elders Thermometer (THERMO)

Elder's Thermometer measures price volatility.

Sources:
    https://www.motivewave.com/studies/elders_thermometer.htm
    https://www.tradingview.com/script/HqvTuEMW-Elder-s-Market-Thermometer-LazyBear/

Calculation:
    Default Inputs:
    length=20, drift=1, mamode=EMA, long=2, short=0.5
    EMA = Exponential Moving Average

    thermoL = (low.shift(drift) - low).abs()
    thermoH = (high - high.shift(drift)).abs()

    thermo = np.where(thermoH > thermoL, thermoH, thermoL)
    thermo_ma = ema(thermo, length)

    thermo_long = thermo < (thermo_ma * long)
    thermo_short = thermo > (thermo_ma * short)
    thermo_long = thermo_long.astype(int)  
    thermo_short = thermo_short.astype(int)

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    long(int): The buy factor
    short(float): The sell factor
    length (int): The  period. Default: 20
    drift (int): The diff period. Default: 1
    mamode (str): Three options: "ema", "sma", or "hma". Default: "ema"
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: thermo, thermo_ma, thermo_long, thermo_short columns.
"""