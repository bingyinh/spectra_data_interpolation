# curve interpolation tool for general use
# By Bingyin Hu
# See how to use in the test section

from serialClass import serial
import numpy as np

class curve_interpolation(object):
    def __init__(self, sorting = 'off'):
        if sorting == 'on':
            self.sorting = True
        else:
            self.sorting = False
        self.sAll = []

    # load spectra data into the object
    def load(self, X, Y, tag, logX=False, logY=False):
        # if we need to sort X and Y based on X
        if self.sorting:
            [sortedX, sortedY] = list(zip(*sorted(zip(X, Y))))
            self.sAll.append(serial(sortedX, sortedY, tag, logX, logY))
        else:
            self.sAll.append(serial(X, Y, tag, logX, logY))

    # a function that takes an array of serial object, 
    # returns True as long as there is a serial object has flag False
    # otherwise returns False
    def proceed(self, sAll):
        for serial in sAll:
            if not serial.flag:
                return True
        return False
    # the function that runs the interpolation
    def run(self):
        if len(self.sAll) < 2:
            raise ValueError("Load the curve_interpolation twice to start.")
        # generate new X axis
        newX = []
        for serial in self.sAll:
            newX += serial.Xins
        newX = sorted(set(newX))
        # interpolate
        for serial in self.sAll:
            serial.Xouts = newX
            serial.computeY()

        # # start running
        # while self.proceed(self.sAll):
        #     nextXPool = []
        #     # find the smaller pointed X
        #     for si in self.sAll:
        #         if not si.flag:
        #             nextXPool.append(si.Xins[si.inPter])
        #     nextX = min(nextXPool)
        #     # add to Xouts
        #     for si in self.sAll:
        #         si.Xouts.append(nextX)
        #         # add corresponding Youts if available, leave placeholder if not
        #         if not si.flag and nextX == si.Xins[si.inPter]:
        #             si.Youts.append(si.Yins[si.inPter]) # add to Youts
        #             # update outPter
        #             si.outPter += 1
        #             # check whether there is a placeholder that has not been interpolated
        #             # if interp is empty, save the current point to leftX, leftY
        #             if len(si.interp) == 0:
        #                 si.leftX = si.Xins[si.inPter]
        #                 si.leftY = si.Yins[si.inPter]
        #             # otherwise, compute the interp using the current point as rightX, rightY
        #             # special case 1 ensures we always have a leftX, leftY
        #             else:
        #                 si.rightX = si.Xins[si.inPter]
        #                 si.rightY = si.Yins[si.inPter]
        #                 while len(si.interp) > 0:
        #                     pt = si.interp.pop(0)
        #                     x0 = si.Xouts[pt]
        #                     y0 = si.intp(x0, si.leftX, si.leftY, si.rightX, si.rightY)
        #                     si.Youts[pt] = y0
        #             si.inPter += 1
        #         else:
        #             # special case 1: first value, compute with two values on the right
        #             if si.outPter == 0:
        #                 nextY = si.intp(nextX, si.Xins[si.inPter], si.Yins[si.inPter],
        #                                 si.Xins[si.inPter+1], si.Yins[si.inPter+1])
        #                 si.Youts.append(nextY)
        #                 si.leftX = nextX
        #                 si.leftY = nextY
        #             else:
        #                 si.Youts.append('PH') # placeholder
        #                 si.interp.append(si.outPter)
        #             si.outPter += 1
        #         # check and update the end flag
        #         if si.inPter >= si.end:
        #             si.flag = True
        # # deal the leftover interpolates
        # for si in self.sAll:
        #     while len(si.interp) > 0:
        #         pt = si.interp.pop(0)
        #         x0 = si.Xouts[pt]
        #         x1 = si.Xouts[pt - 1]
        #         y1 = si.Youts[pt - 1]
        #         x2 = si.Xouts[pt - 2] # our algorithm guarantees pt - 2 is available
        #         y2 = si.Youts[pt - 2] # our algorithm guarantees pt - 2 is available
        #         y0 = si.intp(x0, x1, y1, x2, y2)
        #         si.Youts[pt] = y0

    # exports a dict with structure like
    # {tag: {'X': interpolated X array, 'Y': interpolated Y array}}
    def export(self):
        output = {}
        for si in self.sAll:
            Xouts = si.Xouts
            Youts = si.Youts
            output[si.tag] = {'X': Xouts, 'Y': Youts}
        return output
    
    # exports master curves in one file
    def master_curve(self, ep_csv, epp_csv, mc_file='master_curve.txt',logX=True, logY=True):
        ep = np.loadtxt(ep_csv,delimiter=',')
        epp = np.loadtxt(epp_csv,delimiter=',')
        self.load(ep[:,0], ep[:,1], 'ep', logX, logY)
        self.load(epp[:,0], epp[:,1], 'epp', logX, logY)
        self.run()
        output = np.zeros((len(self.sAll[0].Xouts),3))
        output[:,0] = self.sAll[0].Xouts
        output[:,1] = self.sAll[0].Youts
        output[:,2] = self.sAll[1].Youts
        np.savetxt(mc_file,output)
        print(f"Master curve dumped to {mc_file}")
        return
        
## test
if __name__ == '__main__':
    X1 = [1,1.5,2,4,6]
    Y1 = [1,1.5,2,8,12]
    tag1 = 'tag1'
    X2 = [2,3,4,5,7]
    Y2 = [4,6,8,10,14]
    tag2 = 'tag2'
    X3 = [10, 900]
    Y3 = [0, 890]
    tag3 = 'tag3'
    curve_int = curve_interpolation() # create the curve_interpolation object
    curve_int.load(X1,Y1,tag1) # load the X, Y, tag
    curve_int.load(X2,Y2,tag2) # load at least twice
    curve_int.load(X3,Y3,tag3)
    curve_int.run()
    output = curve_int.export()
    print(output)
