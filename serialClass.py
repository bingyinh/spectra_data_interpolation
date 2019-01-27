# serial object class
# By Bingyin Hu
class serial(object):
    def __init__(self, Xins, Yins, tag):
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
        return y1-(y2-y1)*1.0/(x2-x1)*(x1-x0)