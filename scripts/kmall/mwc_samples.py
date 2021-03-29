from .kmall import Kmall

def samplesToFile(file):
    kmall_file = Kmall(file)
    datagrams = kmall_file.getMWCDatagrams()
    f = open(file + ".samples", 'a')
    f.truncate(0)

    for d in datagrams:
        dgmList = []
        for i in range(0, d.rxInfo.numBeams):
            dataList = d.beamData_p[i].sampleAmplitude05dB_p[:d.beamData_p[i].numSampleData]
            dgmList += dataList
        f.writelines(["%s\n" % item for item in dgmList])
    f.close()
