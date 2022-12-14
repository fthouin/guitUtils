# Classes to store and plot the results of distinct experiments performed on guitar pedals
from waveform import Wave
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pickle
import electrools as et


class freqSweepData():
    '''
    Class to hold frequency sweep data
    '''
    def __init__(self,waveIn,waveOut,freqs,amp):
        '''
        Initialize from lists of input and an output waveforms
        :param self:
        :param waveIn: List of Waveforms associated with the input.
        :param waveOut:  List of Waveforms associated with the output
        :return:
        '''
        self.waveIn=waveIn
        self.waveOut=waveOut
        self.freqs=freqs
        self.amp=amp
    @classmethod
    def fromFile(cls,filename):
        '''
        Initializes from a saved instance
        :param cls:
        :param filename: the path to the filename
        :return:
        '''
        with open(filename,'rb') as input:
            return pickle.load(input)
    def save(self,filename):
        '''
        Saves the content of the object to the provided filename
        :param self: the frequency sweep data object
        :param filename: the name (including path, concluded by .pkl) where to save the data
        :return:
        '''
        with open(filename,'wb') as output:
            pickle.dump(self,output,pickle.HIGHEST_PROTOCOL)
    def linResponse(self):
        '''
        Returns the linear response extracted from the Data held in the frequency sweep.
        The linear response is the complex ratio between the input and output signal at the fundamental frequency
        :return: 
            np.array: frequencies at the which the response is specified
            np.arry: the amplitude of the linear response expressed in dBV
            np.array: the phase of the linear response (in deg)
        '''
        amp=[]
        phase=[]
        for wIn,wOut,freq in zip(self.waveIn,self.waveOut,self.freqs):
            f, sIn = wIn.getPositiveSpectrum()
            f, sOut = wOut.getPositiveSpectrum()
            sTrans = sOut / sIn
            index=np.argmin(np.abs(freq-f))
            amp.append(np.abs(sTrans[index]))
            phase.append(np.angle(sTrans[index],deg=True))
        return self.freqs,et.todBAmp(np.array(amp)),np.array(phase)
    def totalHarmonicDistortion(self):
        '''
        Calculates the total harmonic distortion present in the gathered waveforms.
        It is defined as the ratio of the amplitude contained in the all the harmonics to the amplitude contained in the fundamental (in %)
        Following from http://www.r-type.org/addtext/add183.htm
        :return:
            np.array: frequencies at which the THD is specified
            np.array: THD for that frequency in the input
            np.array: THD for that frequency in the output
        '''
        THDIn=[]
        THDOut=[]
        for wIn,wOut,freq in zip(self.waveIn,self.waveOut,self.freqs):
            f, sIn = wIn.getPositiveSpectrum()
            f, sOut = wOut.getPositiveSpectrum()
            maxHarm=int(np.max(f)/freq)
            indexFond = np.argmin(np.abs(freq - f))
            fundIn=np.abs(sIn[indexFond])
            fundOut=np.abs(sOut[indexFond])
            thdOut=0
            thdIn=0
            for n in range(2,maxHarm):
                index=np.argmin(np.abs(n*freq-f))
                thdIn+=np.abs(sIn[index])**2
                thdOut+=np.abs(sOut[index])**2
            THDIn.append(np.sqrt(thdIn)/fundIn*100)
            THDOut.append(np.sqrt(thdOut)/fundOut*100)
        return self.freqs,THDIn,THDOut

    def freqFreqMap(self,plot=False):
        if plot:
            fsIn, fsOut, corrMap=self.plotfreqFreqMap()
            return fsIn,fsOut,corrMap
        else:
            fsOut=[]
            fsIn=[]
            sOuts=[]
            for wOut,freq in zip(self.waveOut,self.freqs):
                f, sOut = wOut.getPositiveSpectrum()
                fsOut.append(f)
                fsIn.append(freq*np.ones(f.shape))
                sOuts.append(sOut)
            return np.array(fsIn),np.array(fsOut),np.array(sOuts)
    def plotfreqFreqMap(self):
        fsIn, fsOut, corrMap = self.freqFreqMap(plot=False)
        plt.figure()
        Z=np.abs(corrMap)
        plt.pcolormesh(fsIn, fsOut, Z,norm=colors.LogNorm(vmin=Z.min(), vmax=Z.max()),cmap='hot', shading='auto')
        plt.colorbar()
        plt.xlim([20, 20e3])
        plt.xscale('log')
        plt.yscale('log')
        plt.ylim([20, 20e3])
        plt.xlabel('Input frequency (Hz)')
        plt.ylabel('Output frequency (Hz)')
        return fsIn, fsOut, corrMap 

            

        