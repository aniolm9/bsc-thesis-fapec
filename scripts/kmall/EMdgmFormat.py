from ctypes import *

MAX_NUM_TX_PULSES = 9

class EMdgmHeader(Structure):
    _fields_ = [('numBytesDgm', c_uint32),
                ('dgmType', c_uint8 * 4),
                ('dgmVersion', c_uint8),
                ('systemID', c_uint8),
                ('echoSounderID', c_uint16),
                ('time_sec', c_uint32),
                ('time_nanosec', c_uint32)]

class EMdgmMpartition(Structure):
    _fields_ = [('numOfDgms', c_uint16),
                ('dgmNum', c_uint16)]

class EMdgmMbody(Structure):
    _fields_ = [('numBytesCmnPart', c_uint16),
                ('pingCnt', c_uint16),
                ('rxFansPerPing', c_uint8),
                ('rxFanIndex', c_uint8),
                ('swathsPerPing', c_uint8),
                ('swathAlongPosition', c_uint8),
                ('txTransducerInd', c_uint8),
                ('rxTransducerInd', c_uint8),
                ('numRxTransducers', c_uint8),
                ('algorithmType', c_uint8)]

class EMdgmMWCtxInfo(Structure):
    _fields_ = [('numBytesTxInfo', c_uint16),
                ('numTxSectors', c_uint16),
                ('numBytesPerTxSector', c_uint16),
                ('padding', c_int16),
                ('heave_m', c_float)]

class EMdgmMWCtxSectorData(Structure):
    _fields_ = [('tiltAngleReTx_deg', c_float),
                ('centreFreq_Hz', c_float),
                ('txBeamWidthAlong_deg', c_float),
                ('txSectorNum', c_uint16),
                ('padding', c_int16)]

class EMdgmMWCrxInfo(Structure):
    _fields_ = [('numBytesRxInfo', c_uint16),
                ('numBeams', c_uint16),
                ('numBytesPerBeamEntry', c_uint8),
                ('phaseFlag', c_uint8),
                ('TVGfunctionApplied', c_uint8),
                ('TVGoffset_dB', c_int8),
                ('sampleFreq_Hz', c_float),
                ('soundVelocity_mPerSec', c_float)]

class EMdgmMWCrxBeamData(Structure):
    _fields_ = [('beamPointAngReVertical_deg', c_float),
                ('startRangeSampleNum', c_uint16),
                ('detectedRangeInSamples', c_uint16),
                ('beamTxSectorNum', c_uint16),
                ('numSampleData', c_uint16),
                ('detectedRangeInSamplesHighResolution', c_float),
                ('sampleAmplitude05dB_p', POINTER(c_int8)),
                ('samplePhases1_p', POINTER(c_int8)),
                ('samplePhases2_p', POINTER(c_int16))]

class EMdgmMWCrxBeamPhase1(Structure):
    _fields_ = [('rxBeamPhase', c_int8)]

class EMdgmMWCrxBeamPhase2(Structure):
    _fields_ = [('rxBeamPhase', c_int16)]

class EMdgmMWC(Structure):
    _fields_ = [('header', EMdgmHeader),
                ('partition', EMdgmMpartition),
                ('cmnPart', EMdgmMbody),
                ('txInfo', EMdgmMWCtxInfo),
                ('sectorData', EMdgmMWCtxSectorData * MAX_NUM_TX_PULSES),
                ('rxInfo', EMdgmMWCrxInfo),
                ('beamData_p', POINTER(EMdgmMWCrxBeamData))]
