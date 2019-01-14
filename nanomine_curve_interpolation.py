#! /usr/bin/env python
# tanDelta-like spectra data interpolation tool
# By Bingyin Hu, 01/09/2019

from lxml import etree
import os
from curve_interpolation import curve_interpolation
import dicttoxml

class nanomine_curve_interpolation(object):
    def __init__(self, xmlDir):
        self.checkDir(xmlDir)
        self.xmlDir = os.path.normpath(xmlDir)
        self.tree = etree.parse(self.xmlDir)
        self.__initNode__()
        self.emptyTemplate = '''<root><data><description>Computed by NanoMine</description><data><headers><column>X</column><column>Y</column></headers><rows>to be replaced</rows></data></data></root>'''
        # master nodes to store 'AC_DielectricDispersion' (DMA N/A due to schema)
        self.masterNodes = []
        self.masterNodes += self.tree.findall('.//AC_DielectricDispersion')
        self.DEreal = 1 # indicates the default index of Dielectric_Real_Permittivity in AC_DielectricDispersion
        self.DEloss = 2 # indicates the default index of Dielectric_Loss_Permittivity in AC_DielectricDispersion
        self.DEtd = 3 # indicates the default index of Dielectric_Loss_Tangent in AC_DielectricDispersion

    def __initNode__(self):
        self.childNodes = {} # saves etree element
        self.forMissing = {} # saves CIoutput to compute the missing property
        self.Xunit = None # saves unit of X axis
    # the overall run function
    def run(self):
        # loop through the masterNodes to interpolate and make changes to tree
        for masterNode in self.masterNodes:
            self.runOne(masterNode)
            self.__initNode__()
        # write
        self.tree.write('test.xml', encoding="UTF-8", xml_declaration=True)

    # the function to interpolate a single masterNode and save it to the tree
    def runOne(self, node):
        childNodes = []
        # scan the child nodes
        if node.find('Dielectric_Real_Permittivity[data]') is not None:
            self.childNodes['Dielectric_Real_Permittivity'] = node.find('Dielectric_Real_Permittivity[data]')
        if node.find('Dielectric_Loss_Permittivity[data]') is not None:
            self.childNodes['Dielectric_Loss_Permittivity'] = node.find('Dielectric_Loss_Permittivity[data]')
        if node.find('Dielectric_Loss_Tangent[data]') is not None:
            self.childNodes['Dielectric_Loss_Tangent'] = node.find('Dielectric_Loss_Tangent[data]')
        if len(self.childNodes) < 2:
            return
        # if we have more than 2 childNodes available, proceed to init CI
        curve_int = curve_interpolation('on') # create the CI object with sorting
        for tag in self.childNodes:
            curve_int.load(*self.ingest(self.childNodes[tag]))
        curve_int.run()
        CIoutput = curve_int.export()
        for tag in CIoutput:
            childNode = self.childNodes[tag]
            self.updateCurve(childNode, CIoutput[tag])
            self.forMissing[tag] = CIoutput[tag] # save it to self.forMissing
        # add the missing childNode
        self.addCurve(node)

    # data ingest function that takes the etree element and returns an array of
    # X, an array of Y, and a tag
    # the input etree element at the level of 'Dielectric_Real_Permittivity'
    def ingest(self, childNode):
        xlabel = childNode.findall('.//data/data/headers/column')[0]
        ylabel = childNode.findall('.//data/data/headers/column')[1]
        xtext = xlabel.text
        ytext = ylabel.text
        self.Xunit = xtext
        factor = [1, 1] # a flag for percentage unit, especially for tan delta
        if '%' in xtext or 'per cent' in xtext or 'percent' in xtext:
            factor[0] = 0.01
            xlabel.text = xlabel.text.replace('%','').replace('per cent','').replace('percent','')
        if '%' in ytext or 'per cent' in ytext or 'percent' in ytext:
            factor[1] = 0.01
            ylabel.text = ylabel.text.replace('%','').replace('per cent','').replace('percent','')            
        data = childNode.find('.//data/data/rows')
        output = ([], [], childNode.tag) # (X, Y, tag)
        count = 0 # use the count to determine X or Y
        for element in data.iter():
            if element.tag == 'column':
                output[count%2].append(float(element.text)*factor[count%2])
                count += 1
        return output # (X, Y, tag)

    # the function that updates the curve data in the childNode with the output
    # from the curve_interpolation tool
    def updateCurve(self, childNode, CItagDict):
        X = CItagDict['X']
        Y = CItagDict['Y']
        assert(len(X) == len(Y))
        profile_data = []
        for i in xrange(len(X)):
            profile_data.append({'row':({'column':X[i]}, {'column':Y[i]})})
        xmlStr = dicttoxml.dicttoxml(profile_data,custom_root='rows',attr_type=False)
        xmlStr = xmlStr.replace('<item>', '').replace('</item>', '').replace('<item >', '')
        newRows = etree.fromstring(xmlStr)
        # now we have the updated rows, replace the old one
        rowParent = childNode.find('./data/data')
        rowParent.replace(rowParent.find('rows'), newRows)
        return

    # add the missing curve for the masterNode
    def addCurve(self, masterNode):
        # init a new etree element using self.emptyTemplate
        ele = etree.fromstring(self.emptyTemplate)
        # Dielectric_Real_Permittivity missing
        if 'Dielectric_Real_Permittivity' not in self.forMissing:
            # create one for it
            X2 = self.forMissing['Dielectric_Loss_Permittivity']['X']
            Y2 = self.forMissing['Dielectric_Loss_Permittivity']['Y']
            X3 = self.forMissing['Dielectric_Loss_Tangent']['X']
            Y3 = self.forMissing['Dielectric_Loss_Tangent']['Y']
            assert(X2 == X3)
            # compute the new Y
            X1 = X2
            Y1 = []
            for i in xrange(len(Y1)):
                Y1.append(Y2[i]*1.0*Y3[i])
            # update the ele
            ele.tag = 'Dielectric_Real_Permittivity'
            self.updateCurve(ele, {'X': X1, 'Y': Y1})
            # update the header
            ele.findall('.//data/data/headers/column')[0].text = self.Xunit # X
            ele.findall('.//data/data/headers/column')[1].text = 'Dielectric Constant' # Y
            # update masterNode using ele
            if masterNode.find('./Description') is None:
                masterNode.insert(self.DEreal - 1, ele)
            else:
                masterNode.insert(self.DEreal, ele)
        # Dielectric_Loss_Permittivity missing
        if 'Dielectric_Loss_Permittivity' not in self.forMissing:
            # create one for it
            X1 = self.forMissing['Dielectric_Real_Permittivity']['X']
            Y1 = self.forMissing['Dielectric_Real_Permittivity']['Y']
            X3 = self.forMissing['Dielectric_Loss_Tangent']['X']
            Y3 = self.forMissing['Dielectric_Loss_Tangent']['Y']
            assert(X1 == X3)
            # compute the new Y
            X2 = X1
            Y2 = []
            for i in xrange(len(Y1)):
                Y2.append(Y1[i]*1.0/Y3[i])
            # update the ele
            ele.tag = 'Dielectric_Loss_Permittivity'
            self.updateCurve(ele, {'X': X2, 'Y': Y2})
            # update the header
            ele.findall('.//data/data/headers/column')[0].text = self.Xunit # X
            ele.findall('.//data/data/headers/column')[1].text = 'Loss Permittivity' # Y
            # update masterNode using ele
            if masterNode.find('./Description') is None:
                masterNode.insert(self.DEloss - 1, ele)
            else:
                masterNode.insert(self.DEloss, ele)
        # Dielectric_Loss_Tangent missing
        if 'Dielectric_Loss_Tangent' not in self.forMissing:
            # create one for it
            X1 = self.forMissing['Dielectric_Real_Permittivity']['X']
            Y1 = self.forMissing['Dielectric_Real_Permittivity']['Y']
            X2 = self.forMissing['Dielectric_Loss_Permittivity']['X']
            Y2 = self.forMissing['Dielectric_Loss_Permittivity']['Y']
            assert(X1 == X2)
            # compute the new Y
            X3 = X1
            Y3 = []
            for i in xrange(len(Y1)):
                Y3.append(Y1[i]*1.0/Y2[i])
            # update the ele
            ele.tag = 'Dielectric_Loss_Tangent'
            self.updateCurve(ele, {'X': X3, 'Y': Y3})
            # update the header
            ele.findall('.//data/data/headers/column')[0].text = self.Xunit # X
            ele.findall('.//data/data/headers/column')[1].text = 'Tan Delta' # Y
            # update masterNode using ele
            if masterNode.find('./Description') is None:
                masterNode.insert(self.DEtd - 1, ele)
            else:
                masterNode.insert(self.DEtd, ele)
        return


    # check the input xml directory
    def checkDir(self, xmlDir):
        if os.path.splitext(xmlDir)[1].lower() != '.xml':
            raise Exception('Please include the xml extension in the input.')
        return

## test
if __name__ == '__main__':
    # xmlDir = 'D://Dropbox/DIBBS/linda_JAPD/data/L106_S3_Shen_2007.xml-5b71eb00e74a1d7c81bec6c7-5b71ebe4e74a1d7c81bec6f6.xml'
    xmlDir = 'D://Dropbox/DIBBS/linda_JAPD/data/L143_S3_Hui_2013.xml-5b71eb00e74a1d7c81bec6c7-5b72e778e74a1d68f48b2d6b.xml'
    nmCI = nanomine_curve_interpolation(xmlDir)
    nmCI.run()