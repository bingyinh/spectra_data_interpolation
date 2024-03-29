# serial object class
# By Bingyin Hu
import numpy as np

class serial(object):
    def __init__(self, Xins, Yins, tag, logX=False, logY=False):
        # check length of Xins, Yins
        if len(Xins) < 2:
            raise ValueError("The length of input X array must be greater than 2.")
        if len(Yins) < 2:
            raise ValueError("The length of input Y array must be greater than 2.")
        if len(Xins) != len(Yins):
            raise ValueError("The length of input X and Y array must match.")
        # initialize parameters
        self.leftX = None # the X value to the left of the pointer
        self.leftY = None # the Y value to the left of the pointer
        self.rightX = None # the X value to the right of the pointer
        self.rightY = None # the Y value to the right of the pointer
        self._Xins = list(Xins) # the input X value series
        self._Yins = list(Yins) # the input Y value series
        self.Xouts = [] # the output X value series
        self.Youts = [] # the output Y value series
        self.tag = tag # for nm, corresponding to the keys in self.available
        self.interp = [] # the index of Ys that need to be interpolated
        self.inPter = 0 # pointer to Xins, Yins
        self.outPter = 0 # pointer to Xouts, Youts
        self.end = len(self._Xins) # raise the end flag when in pointer >= end
        self.flag = False
        self.logX = logX
        self.logY = logY
        # save a dict of {X:Y}
        self.XinDict = dict(zip(self._Xins,self._Yins))
    @property
    def Xins(self):
        return self._Xins
    @property
    def Yins(self):
        return self._Yins
    # returns the interpolated y0
    # x0: the x of the point to be interpolated
    # x1, y1, x2, y2: coordinates of the known points
    def intp(self, x0, x1, y1, x2, y2):
        # print('x0:%f, x1:%f, y1:%f, x2:%f, y2:%f' %(x0,x1,y1,x2,y2))
        if self.logX:
            x0 = np.log10(x0)
            x1 = np.log10(x1)
            x2 = np.log10(x2)
        if self.logY:
            y1 = np.log10(y1)
            y2 = np.log10(y2)
            return 10**(y1-(y2-y1)*1.0/(x2-x1)*(x1-x0))
        else:
            return y1-(y2-y1)*1.0/(x2-x1)*(x1-x0)

    # returns y corresponding to the given x, may need interpolation
    def yAtX(self, givenX, leftIndex, sorting = 'off'):
        y = None # init y
        if sorting != 'off':
            # sort the serial based on X
            [self._Xins, self._Yins] = list(zip(*sorted(zip(self._Xins, self._Yins))))
        # case 1: X smaller than the smallest Xins
        if givenX < self._Xins[0]:
            y = self.intp(givenX, self._Xins[0], self._Yins[0],
                                  self._Xins[1], self._Yins[1])
        # case 2: X larger than the largest Xins
        elif givenX > self._Xins[-1]:
            y = self.intp(givenX, self._Xins[-2], self._Yins[-2],
                                  self._Xins[-1], self._Yins[-1])
        # general case: X is within the range of Xins
        else:
            # leftIndex = 0 # init leftIndex
            # for i in range(len(self._Xins)):
            #     if self._Xins[i] > givenX:
            #         leftIndex = i - 1
            #         break
            rightIndex = leftIndex + 1
            y = self.intp(givenX, self._Xins[leftIndex], self._Yins[leftIndex],
                                  self._Xins[rightIndex], self._Yins[rightIndex])
        return y

    def computeY(self):
        if len(self.Xouts) == 0:
            print("Xouts not loaded! Abort!")
            return
        # keep track of the current position of x in Xins
        left = -1
        for i,x in enumerate(self.Xouts):
            # x exists in Xin, use the original y
            if x in self.XinDict:
                self.Youts.append(self.XinDict[x])
                # update the position of x in Xins
                left += 1
            # x does not exist in Xin, call yAtX
            else:
                self.Youts.append(self.yAtX(x, left))

# Test section
if __name__ == '__main__':
    X1 = [1,2,3,4]
    Y1 = [1,2,3,4]
    tag1 = 'tag1'
    s1 = serial(X1, Y1, tag1)
    assert(s1.yAtX(0) == 0)
    assert(s1.yAtX(1) == 1)
    assert(s1.yAtX(2.5) == 2.5)
    assert(s1.yAtX(4) == 4)
    assert(s1.yAtX(5) == 5)