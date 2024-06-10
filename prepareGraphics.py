
MAX_VALUE_ADC = 16383 # 14 bits, 0x3fff
UFAC = 0.00115787 # Relation between sample value and actual voltage.
                  #  U = ns * (5 *77,4/20,4)/16384 =  1,15787* 10^-3 = 0,00115787
RAW_DATA_FILE = "SMPLOG3_240523.txt"
NOMINAL_FS = 1 # The nominal sampling time in seconds
DISRUPT_FAC = 0.15 # (15%) Factor used to define if two intervals are consecutive or disrupted
class graphInterval:
    def __init__(self, interval, startTime, samples, compFs):
        self.intervalNo = interval     # intervals numbered 1, ...
        self.startTime = startTime     # ux time start
        self.samples = samples         # number of samples
        # When timeStamp between two consecutive intervals differs in expected number of samples of the time-interval
        #  compFs is calculated to make timeStamps better in synch with each sample. A larger difference than DISRUPT_FAC is
        #  defined to be a disruption between the intervals
        self.compFs = compFs           # compensated sampling time
        self.graphX = []               # the x-axis result list
        self.graphXux = []             # the x-axis result list in unixtimestamps
        self.graphY = []               # the y-axis result in seconds

class graph:
    def __init__(self, inFile, intervals, samples, nomFs, outFile):
        self.inFile = inFile           # sample log file name and path
        self.intervals = intervals     # number of intervals
        self.samples = samples         # total nuber of samples
        self.nomFs = nomFs             # nominal sampling time in [s]
        self.outFile = outFile         # Some kind of outfile
    def content(self):
        print(self.inFile, self.intervals, self.samples, self.outFile)

from matplotlib import pyplot as plt
import numpy as np
import datetime

with open(RAW_DATA_FILE) as datasource:
    rawData = datasource.readlines()

print("Length of raw data is : " + str(len(rawData)) + " elements")


# Extract timestamps
timeStamps = []
for i in range(len(rawData)):
    val = int(rawData[i])
    if val > MAX_VALUE_ADC:
        timeStamps.append(val)

# Extract samples
sampleCnt = []
samples = 0
for i in range(len(rawData)-1):
    val = int(rawData[i+1])
    if val <= MAX_VALUE_ADC:
        samples += 1
    else:
        sampleCnt.append(samples)
        samples = 0
sampleCnt.append(samples)

# Check the sum of elements are correct, Sum of raw data elements - number of timestamps = sum of samplsCn
if (len(rawData) - len(timeStamps) != sum(sampleCnt)):
    print('Error in element handling!')

# Create Graph object
graph = graph(RAW_DATA_FILE, len(timeStamps), sum(sampleCnt), NOMINAL_FS, "outFileName.txt")
graph.content() # prints content of graph object

# Create interval objects
intervalList = []
for i in range(len(timeStamps)):
    intervalList.append(graphInterval(i+1, timeStamps[i], sampleCnt[i], 1.0))

# Read the sample values to the interval list
checkNmbSamples = 0
rawDataIndex = 0
for i in range(len(intervalList)):
    rawDataIndex += 1  # Skip timestamp value
    for nmbSamples in range(intervalList[i].samples):
        intervalList[i].graphY.append(UFAC * float(rawData[rawDataIndex]))
        checkNmbSamples += 1
        rawDataIndex += 1


#print(checkNmbSamples)

# Calculate the compensated fs
fs = 0
for i in range(len(intervalList) - 1):
    intervalList[i].compFs = float((float(intervalList[i + 1].startTime) - float(intervalList[i].startTime)) / float(intervalList[i].samples))
    if (intervalList[i].compFs > NOMINAL_FS + DISRUPT_FAC):
        intervalList[i].compFs = 1.0


# Print all interval objects
for i in range(len(intervalList)):
    print(intervalList[i].intervalNo, intervalList[i].samples, intervalList[i].startTime, intervalList[i].compFs)

#Create the compensated x-axes
checkNmbSamples = 0
fs = 0
timeStamp = 0
for i in range(len(intervalList)):
    timeStamp = intervalList[i].startTime
    fs = intervalList[i].compFs
    for nmbSamples in range(intervalList[i].samples):
        intervalList[i].graphXux.append(int(round(timeStamp)))
        #timeStamp += fs + NOMINAL_FS
        timeStamp += fs

# f = open("timeStampFileAfterCompNew.txt", "w")
# for i in range(len(intervalList)):
#     for nmbSamples in range(intervalList[i].samples):
#         f.write(f"\n{intervalList[i].graphXux[nmbSamples]}")
# f.close()

# Create x-axis time in seconds
for i in range(len(intervalList)):
    # Create time axis in seconds, extracting seconds from unixtime
    timeStamp = datetime.datetime.fromtimestamp(intervalList[i].startTime)
    ts = int(timeStamp.strftime('%S'))
    fs = intervalList[i].compFs
    for nmbSamples in range(intervalList[i].samples):
        intervalList[i].graphX.append(int(round(ts)))
        ts += fs
    plt.plot(intervalList[i].graphX, intervalList[i].graphY, color='r', linestyle='--', marker='.')
    plt.xlabel(timeStamp.strftime('%Y-%m-%d %H:%M:%S'))
    #myVar = plt.axes.Axes.set_axis_locator
    plt.show()




