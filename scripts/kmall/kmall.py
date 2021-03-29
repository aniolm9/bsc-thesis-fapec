from .EMdgmFormat import *
from array import array
import sys
import os

'''
Class to interact with .kmall/.kmwcd files.
'''
class Kmall():
    def __init__(self, filename):
        self.filename = filename if os.path.exists(filename) else sys.exit(1)
        self.filesize = os.path.getsize(self.filename)
        self.f = open(self.filename, 'rb')
        self.__position = 0
        self.__buffer = bytearray()
        self.__samples = bytearray()
    
    '''
    Returns the next datagram in the file
    as a bytes string.
    '''
    def nextDatagram(self):
        header = EMdgmHeader()
        self.f.seek(self.__position)
        self.f.readinto(header)
        self.f.seek(self.__position)
        self.__position += header.numBytesDgm
        self.__buffer = self.f.read(header.numBytesDgm)
        return self.__buffer
    
    '''
    Given a filename this method finds its size and the percentage of use
    of every datagram.
    '''
    def getDatagramsSize(self, verbose=False):
        result = {}
        read = 0
        max_dgm_size = 0
        while self.__position < self.filesize:
            header = EMdgmHeader.from_buffer_copy(self.nextDatagram()[:sizeof(EMdgmHeader)])
            max_dgm_size = max(max_dgm_size, header.numBytesDgm)
            read += header.numBytesDgm
            dtype = bytes(header.dgmType).decode('ascii')
            if verbose:
                print(dtype)
                print(header.numBytesDgm)
            result[dtype] = header.numBytesDgm if dtype not in result.keys() else result[dtype] + header.numBytesDgm
        result = {k: round(v*100 / self.filesize, 3) for k, v in result.items()}
        return result, max_dgm_size

    '''
    This method returns a list with all the EMdgmMWC
    datagrams in the file.
    '''
    def getMWCDatagrams(self):
        datagrams = []
        while self.__position < self.filesize:
            header = EMdgmHeader.from_buffer_copy(self.nextDatagram()[:sizeof(EMdgmHeader)])
            if bytes(header.dgmType).decode('ascii') == "#MWC":
                # Read datagram bytes and parse them to the struct
                mwc = EMdgmMWC.from_buffer_copy(self.__buffer)
                mwc.txInfo = self.getTxInfo()
                mwc.sectorData = self.getSectorData()
                mwc.rxInfo = self.getRxInfo()
                mwc.beamData_p = self.getBeamData() 
                datagrams.append(mwc)
        return datagrams
    
    '''
    Returns the EMdgmMWCtxInfo struct from
    a EMdgmMWC datagram.
    '''
    def getTxInfo(self):
        # We convert bytes to a MWC datagram
        datagram = EMdgmMWC.from_buffer_copy(self.__buffer)
        # Then we find the EMdgmMWCtxInfo substruct
        txStart = sizeof(EMdgmHeader) + sizeof(EMdgmMpartition) + datagram.cmnPart.numBytesCmnPart
        return EMdgmMWCtxInfo.from_buffer_copy(self.__buffer[txStart:txStart+sizeof(EMdgmMWCtxInfo)])
    
    '''
    Returns an array of length MAX_NUM_TX_PULSES with
    numTxSectors EMdgmMWCtxSectorData.
    '''
    def getSectorData(self):
        # We convert bytes to a MWC datagram
        datagram = EMdgmMWC.from_buffer_copy(self.__buffer)
        # Then we find the EMdgmMWCtxSectorData substruct
        txInfo = self.getTxInfo()
        txStart = sizeof(EMdgmHeader) + sizeof(EMdgmMpartition) + datagram.cmnPart.numBytesCmnPart
        sectorEnd = txStart + txInfo.numBytesTxInfo
        sectors = []
        for i in range(0, txInfo.numTxSectors):
            sectorStart = sectorEnd
            sectorEnd = sectorStart + txInfo.numBytesPerTxSector
            sectors.append(EMdgmMWCtxSectorData.from_buffer_copy(self.__buffer[sectorStart:sectorEnd]))
        return (EMdgmMWCtxSectorData * MAX_NUM_TX_PULSES)(*sectors)
    
    '''
    Returns the EMdgmMWCrxInfo struct from
    a EMdgmMWC datagram.
    '''
    def getRxInfo(self):
        # We convert bytes to a MWC datagram
        datagram = EMdgmMWC.from_buffer_copy(self.__buffer)
        # We need to find txInfo datagram
        txInfo = self.getTxInfo()
        txStart = sizeof(EMdgmHeader) + sizeof(EMdgmMpartition) + datagram.cmnPart.numBytesCmnPart
        # Then we find the EMdgmMWCrxInfo substruct
        rxStart = txStart + txInfo.numBytesTxInfo + txInfo.numTxSectors * sizeof(EMdgmMWCtxSectorData)
        return EMdgmMWCrxInfo.from_buffer_copy(self.__buffer[rxStart:rxStart+sizeof(EMdgmMWCrxInfo)])

    '''
    Returns an array of EMdgmMWCrxBeamData struct from
    an EMdgmMWC datagram. Each EMdgmMWC has
    "numBeams" EMdgmMWCrxBeamData.
    '''
    def getBeamData(self):
        # We convert bytes to a MWC datagram
        datagram = EMdgmMWC.from_buffer_copy(self.__buffer)
        # We need to find txInfo and rxInfo datagram
        txInfo = self.getTxInfo()
        txStart = sizeof(EMdgmHeader) + sizeof(EMdgmMpartition) + datagram.cmnPart.numBytesCmnPart
        rxInfo = self.getRxInfo()
        rxStart = txStart + txInfo.numBytesTxInfo + txInfo.numTxSectors * sizeof(EMdgmMWCtxSectorData)
        # Then we find the EMdgmMWCrxBeamData substruct
        beams = []
        beamEnd = rxStart + rxInfo.numBytesRxInfo
        i = 0
        while i < rxInfo.numBeams:
            beamStart = beamEnd
            # Get beam data information
            beamData = EMdgmMWCrxBeamData.from_buffer_copy(self.__buffer[beamStart:beamStart+sizeof(EMdgmMWCrxBeamData)])
            beamEnd = beamStart + rxInfo.numBytesPerBeamEntry + beamData.numSampleData
            # Find beam samples and a pointer to them in the struct
            samples = array('b', self.__buffer[beamStart + rxInfo.numBytesPerBeamEntry:beamEnd])
            beamData.sampleAmplitude05dB_p = (c_int8 * beamData.numSampleData).from_buffer(samples)
            # Check if there is phase information in the datagram
            if rxInfo.phaseFlag == 1:
                phaseStart = beamEnd
                phases = self.__buffer[phaseStart:phaseStart + sizeof(EMdgmMWCrxBeamPhase1) * beamData.numSampleData]
                beamData.samplePhases1_p = (c_int8 * beamData.numSampleData)(*phases)
            elif rxInfo.phaseFlag == 2:
                phaseStart = beamEnd
                phases = self.__buffer[phaseStart:phaseStart + sizeof(EMdgmMWCrxBeamPhase2) * beamData.numSampleData]
                beamData.samplePhases2_p = (c_int16 * beamData.numSampleData)(*phases)
            beams.append(beamData)
            i += 1
        return (EMdgmMWCrxBeamData * rxInfo.numBeams)(*beams)
