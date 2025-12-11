from enum import IntEnum


class SoilTextureID(IntEnum):
    SAND = 1
    LOAMY_SAND = 2
    SANDY_LOAM = 3
    LOAM = 4
    SILT_LOAM = 5
    SILT = 6
    SANDY_CLAY_LOAM = 7
    CLAY_LOAM = 8
    SILTY_CLAY_LOAM = 9
    SANDY_CLAY = 10
    SILTY_CLAY = 11
    CLAY = 12


class AgroforestryTypeID(IntEnum):
    BLOCK = 1
    BOUNDARY = 2
    INTERCROPPING = 3
    MOSAIC = 4
