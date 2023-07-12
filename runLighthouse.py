#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Input (of runLighthouse): csv File with a list of Urls """


import subprocess
import json
import csv
from pathlib import Path
from builtwith import builtwith
import socket
import urllib
import requests
import argparse


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
        if not Path('out/').exists(): Path('out/').mkdir(parents=True, exist_ok=True)
        for outFn in Path("out/").rglob("*"): outFn.unlink()
        if not Path('ok/').exists(): Path('ok/').mkdir(parents=True, exist_ok=True)
        for okFn in Path("ok/").rglob("*"): okFn.unlink()
        if not Path('nok/').exists(): Path('nok/').mkdir(parents=True, exist_ok=True)
        for nokFn in Path("nok/").rglob("*"): nokFn.unlink()
        with open('out/ok.csv', 'w') as csvFn:
            techSheet = csv.writer(csvFn, delimiter=';')
            techSheet.writerow(['org', 'IP', 'site', 'diff', 'techstack'])
        with open('out/nok.csv', 'w') as csvFn:
            techSheet = csv.writer(csvFn, delimiter=';')
            techSheet.writerow(['org', 'IP', 'site', 'diff', 'techstack'])
        self.notAvailable = 0
        self.available = 0
        self.numberOk = 0
        self.numberNotOk = 0

    def calcKpi(self):
        """ Performing measurement for each site, calculate the KPI and return output string. """
        results = [(self.analyseSite(u), u) for u in self.urls]
        outStr = ""
        for r, u in results:
            if r == -2:
                outStr += "(Partly) not available: " + str(u) + "<br>"
                self.notAvailable += 1
            else:
                self.available += 1
                if r > diffParameter: self.numberNotOk += 1
                else: self.numberOk += 1
        if self.numberOk + self.numberNotOk != self.available: print("Simple check for availability failed!")
        print("=============================== ")
        outStr += "available: " + str(self.available) + ", ok by 5%: " + str(self.numberOk) + ", not ok: " + str(self.numberNotOk) + "<br>"
        if self.available == 0: self.available = 1.0
        kpi = round(self.numberOk / self.available * 100.0)
        outStr += "KPI: " + str(kpi)
        print(outStr.replace("<br>", '\n'))
        with open('kpi.txt', 'w') as fnHandle:
            print(outStr, file=fnHandle)
        with open('status.txt', 'w') as fnHandle:
            print("Finished", file=fnHandle)
        return outStr

    def analyseUrlStr(self, site: str):
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
    def analyseSite(self, site: str):
        """ Doing the measurement for one site. """
        proto, site, fnName = self.analyseUrlStr(site)
        print("Please, be patient. Currently working on " + site)
        with open('status.txt', 'w') as fnHandle:
            print(site, file=fnHandle)
        # measurement instance for site
        sm = lighthouseSiteResult(site)
        # mobile measurement
        subprocess.run(['lighthouse "' + proto + site + '" --quiet --chrome-flags="--headless --disable-dev-shm-usage --disable-storage-reset --no-sandbox" --output json --output-path json/' + fnName + '-mobile.json --form-factor="mobile"'], shell=True)
        try:
            with open('json/' + fnName + '-mobile.json', 'r') as fnHandle:
                lighthouseReportDict = json.load(fnHandle)
        except:
            print("json/" + fnName + "-mobile.json has not been written")
            return -2
        for k in lighthouseReportDict['categories'].keys():
            sm.mobile[k] = lighthouseReportDict['categories'][k]['score']
        # desktop measurement
        subprocess.run(['lighthouse "' + proto + site + '" --quiet --chrome-flags="--headless --disable-dev-shm-usage --disable-storage-reset --no-sandbox" --output json --output-path json/' + fnName + '-desktop.json --preset="desktop" --form-factor="desktop"'], shell=True)
        try:
            with open('json/' + fnName + '-desktop.json', 'r') as fnHandle:
                lighthouseReportDict = json.load(fnHandle)
        except:
            print("json/" + fnName + "-mobile.json has not been written")
            return -2
        for k in lighthouseReportDict['categories'].keys():
            sm.desktop[k] = lighthouseReportDict['categories'][k]['score']
        # kpi contribution
        if not None in sm.desktop.values() and not None in sm.mobile.values():
            diff = sm.doCalc()
        else:
            diff = -2  # technical value
        return diff
