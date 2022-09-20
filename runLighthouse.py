""" Input (of runLighthouse): csv File with a list of Urls """


import os
import json
import csv
from pathlib import Path


diffParameter = 0.05  # parameter defined in the kpi characteristics

class lighthouseSiteResult:
    def __init__(self, site):
        self.diffParameter = diffParameter
        #
        self.site = site
        self.desktop = {}
        self.mobile = {}
        self.desktopMean5 = 0.0
        self.mobileMean5 = 0.0
        self.diff5 = 0.0

    def calcMean(self, categoValues, withPWA=True):
        tsum = 0
        for k in categoValues.keys():
            tsum += categoValues[k]
        return tsum / 5.0

    def doCalc(self):
        """ Mean et al. """
        self.desktopMean5 = self.calcMean(self.desktop)
        self.mobileMean5 = self.calcMean(self.mobile)
        self.diff5 = self.desktopMean5 - self.mobileMean5
        return self.diff5

class runLighthouse:
    """ Run KPI measurement
        Input: Urls for measurement in csv file
        Output: String reporting KPI (and number of available sites) """
    def __init__(self, file):
        self.urls = []
        if file != '':
            with open(file) as csvFile:
                csvUrlsFile = csv.reader(csvFile, delimiter = ';')
                for row in csvUrlsFile:
                    # print(row)
                    self.urls.append(row[1])  # URL in the second column
        if not Path('json/').exists(): Path('json/').mkdir(parents=True, exist_ok=True)
        for jsonFn in Path("json/").rglob("*.json"): jsonFn.unlink()
        self.notAvailable = 0
        self.available = 0
        self.numberOk = 0
        self.numberNotOk = 0

    def calcKpi(self):
        """ Calling measurement for each site, calculate the KPI and return output string. """
        results = [(self.analyseSite(u), u) for u in self.urls]
        outStr = ""
        for r, u in results:
            if r == -2:
                outStr += "(Partly) not available: " + str(u) + "<br>"
                self.notAvailable += 1
            else:
                self.available += 1
                if r > diffParameter: self.numberNotOk += 1  # using paramater defined in kpi characteristics
                else: self.numberOk += 1
        outStr += "available: " + str(self.available) + ", ok by 5%: " + str(self.numberOk) + ", not ok: " + str(self.numberNotOk) + "<br>"
        if self.available == 0: self.available = 1.0
        kpi = round(self.numberOk / self.available * 100.0)
        outStr += "KPI: " + str(kpi)
        return outStr

    def analyseUrlStr(self, site):
        """ Analyse Url string regarding protocal, containing a slash. """
        proto = "https://"
        if site.startswith("https://"):
            site = site[8:]
        if site.startswith("http://"):
            site = site[7:]
            proto = "http://"
        slashPosition = site.find('/')
        if slashPosition >= 0: fnName = site[:slashPosition]
        else: fnName = site
        return  proto, site, fnName
    def analyseSite(self, site):
        """ Doing the measurement for one site. """
        proto, site, fnName = self.analyseUrlStr(site)
        print("############################### " + site)
        # measurement instance for site
        sm = lighthouseSiteResult(site)
        # mobile measurement
        os.system('lighthouse "' + proto + site + '" --chrome-flags="--headless" --output json --output-path json/' + fnName + '-mobile.json --form-factor="mobile"')
        with open('json/' + fnName + '-mobile.json', 'r') as fnHandle:
            lighthouseReportDict = json.load(fnHandle)
        for k in lighthouseReportDict['categories'].keys():
            sm.mobile[k] = lighthouseReportDict['categories'][k]['score']
        # desktop measurement
        os.system('lighthouse "' + proto + site + '" --chrome-flags="--headless" --output json --output-path json/' + fnName + '-desktop.json --preset="desktop" --form-factor="desktop"')
        with open('json/' + fnName + '-desktop.json', 'r') as fnHandle:
            lighthouseReportDict = json.load(fnHandle)
        for k in lighthouseReportDict['categories'].keys():
            sm.desktop[k] = lighthouseReportDict['categories'][k]['score']
        # kpi contribution
        if not None in sm.desktop.values() and not None in sm.mobile.values():
            diff = sm.doCalc()
        else:
            diff = -2  # technical value
        return diff
