#!/usr/bin/env python
# encoding: utf-8

# This module is using pdfplumber lib to parse NewDay credit card statements
# and visualize the result using mathplotlib bar
# usage: python statement_stats.py <statement pdf file>

import pdfplumber
import re
import sys
import matplotlib.pyplot as plt
from os.path import exists

file_exists = exists(sys.argv[1])

if not file_exists:
    print("File " + sys.argv[1] + " does not exist");
    exit(-1)

with pdfplumber.open(sys.argv[1]) as pdf:
    entries = {}
    total = 0

    if not pdf.pages:
        print("This does not look like a valid NewDay Statement")
        exit(-1)

    for page in pdf.pages:
            pdfstr = page.extract_text(x_tolerance=3, y_tolerance=3)
            # NewDay statements normally come in a format
            # 02 Dec 2021   <reference number>    Organisation       value
            x = re.findall("[^0-9]{1}[0-9]{0,2}[ ]+[a-zA-Z]{1,8}[ ]+202[1-9][ ]+[0-9]+[ ]+.*[0-9]+[\.]{0,1}[0-9]{0,2}", pdfstr) #dd Month yyyy
            for val in x:
                balance = val.encode("ascii", "ignore").decode()

                # Ignore credit card repayments. those are irrelevant fo the monthly balance
                if "Payment Received" in balance:
                    continue

                balance = balance.split(" ")
                balance = balance[4:]
                balance = "".join(balance).replace("\n","")
                entry = balance.rsplit("+", 1) if "+" in balance else balance.rsplit("-",1)
                entry[1]  = "+" + entry[1] if "+" in balance else "-" + entry[1]
                #remove commas from big numbers ( > 1000)
                entry[1] = entry[1].replace(",","")

                total += float(entry[1])
                if entry[0] in entries:
                    entries[entry[0]] = entries[entry[0]] + float(entry[1])
                else:
                    entries[entry[0]] = float(entry[1])

    #round numbers up
    for k in entries:
       entries[k] = round(entries[k], 2)

    total = round(total,2)
    print("Total spent: ", total)
    names = list(entries.keys())
    values = list(entries.values())

    negative_indices = [idx for idx in range(len(values)) if values[idx] < 0]

    barlist = plt.bar(range(len(names)), values, tick_label=names, color='r')
    for idx in negative_indices:
      barlist[idx].set_color('g')

    for i in range(len(names)):
        plt.text(i-0.5,values[i],values[i])

    plt.title("Overall spent: " + str(total))
    plt.xticks(rotation=-90)
    plt.show()
