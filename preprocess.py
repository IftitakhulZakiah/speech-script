#!/usr/bin/env python

import re
import sys
import random
import string
import os
import codecs
from collections import Counter
from multiprocessing import Pool, cpu_count
from argparse import ArgumentParser

# TODO: add function to process roman numerals, units, and currency
#       improve acronyms parser

# LIST OF REGEX FOR EACH CASE
# any numeral
re_num = re.compile('\d')

#re_dash = re.compile(r'[\d]*[-]{0,1}[\d]+')
# dash = [, r'\-\-']
re_dash = re.compile(r'[\-]+')

# numbers, decimal (. or ,), dates(/)
form = [r'(?<![a-zA-Z])[\d]*[\.,]{0,1}[\d\.,]{0,}[\d]', \
        r'(?<![a-zA-Z])[\d]*[\.,]{0,1}[\d\.,]{0,}[\d](?![a-zA-Z])', \
        r'[\d]*[\.,]{0,1}[\d\.]{0,}[\d](?![a-zA-Z])']
re_form = re.compile('|'.join(form))

# roman numerals
re_roman = re.compile(r'\b[IVX]+\b')

# separator
re_sep = re.compile(r'[-\.,\/](?!$)')

# date
re_date = re.compile(r'\(([\d]*[\/][\d]+\/)')

# caps-lock, for acronym
re_caps = re.compile(r'\b[0-9]*[A-Z]+[A-Z0-9]*\b')

# parentheses
re_parnth = re.compile(r'\([\w ,\-\.%@#&*\$\/]+\)')

# internet related texts (websites, username, email, tags)
intr=[r'\B#[a-z0-9]+\b', r'\B@[a-z0-9_]+\b', \
        r'\b[a-z0-9_\.]{3}[a-z0-9_\.]*@[a-z0-9]+\.[a-z]+[a-z\.]*\b', \
        r'\b(?:http\://)?[a-z-0-9]{3}[a-z0-9]*\.[a-z0-9\./]+\b']
re_intr = re.compile('|'.join(intr))

# numbers that have to be pronounced sequentially e.g phone numbers, zipcode 
phone=[r'\B\+[0-9]{2}[0-9]*[0-9\- ]*[0-9]\b', \
        r'\B\([0-9]{2}[0-9]*\)[0-9\- ]*[0-9]\b',
        r'\b(?<!\.)[0-9]{1,3}[\- ][0-9\- ]+[0-9]\b',
        r'\b[0-9]{5}[0-9]*\b',
        r'\B\*[0-9#\*]+\B']
re_phone = re.compile('|'.join(phone))

# units
un=[r'\b[kKhdcm]?m[23]?\b', r'\b[kKhdcm]?g\b', \
        r'\b[kKhdcm]?l\b', r'\bcc\b', r'\b[MGKkhdcm]?Hz\b', \
        r'\b[TMGKtmgk]?[Bb]\b']
re_units = re.compile('|'.join(un))

# degree
deg = ["H.", "Hj.", "Ph.D","Ir.", "Drs.", "Dra.", "Alm."]
re_degree = re.compile('|'.join(deg))

# time zone
re_time_zone = re.compile(r'WI[BT]A*')

# currency, but only $ and Rp
r = [r'\bRp[\. ]*[0-9\.,]*[0-9\-]+\b', r'\B\$[\.,0-9]*[0-9]\b',\
        r'\bUSD[\.,0-9]*[0-9]\b', r'\bUS\$[0-9]+[\.,0-9]*[0-9]\b']
base = ['ribu', 'juta', 'milyar', 'miliar', 'triliun', 'trilyun', 'kuadriliun']
pat_cur = [x + ' ' + y for x in r for y in base] + r
re_curr = re.compile('|'.join([x + ' ' + y for x in r for y in base] + r))

#re_curr = re.compile('|'.join([r'\brp[\. ]*[0-9]+ trilyun', r'\$']))

# dictionary storing Indonesian pronunciation of numerals
nomor = {
    '0': 'nol',
    '1': 'satu',
    '2': 'dua',
    '3': 'tiga',
    '4': 'empat',
    '5': 'lima',
    '6': 'enam',
    '7': 'tujuh',
    '8': 'delapan',
    '9': 'sembilan'
}

base = {
    1: 'ribu',
    2: 'juta',
    3: 'milyar',
    4: 'triliun',
    5: 'kuadriliun',
}

base_units = {
    'M': 'mega',
    'G': 'giga',
    'g': 'giga',
    'T': 'tera',
    't': 'tera',
    'K': 'kilo',
    'k': 'kilo',
    'h': 'hekto',
    'da': 'deka',
    'd': 'desi',
    'c': 'senti',
    'm': 'mili',
    'H': 'hertz'
}

units = {
    'g': 'gram',
    'l': 'liter',
    'm': 'meter',
    'ha': 'hektar',
    'c': 'meter kubik',
    'Hz': 'hertz',
    'z': '',
    'B': 'byte',
    'b': 'bit'
}

pow_units = {
    '2': 'persegi',
    '3': 'kubik',
}

currency = {
    'Rp': 'rupiah ',
    '$': 'dolar ',
    'USD': 'dolar amerika ',
    'US$': 'dolar amerika '
}

bulan = {
    0: 'oktober',
    1: 'januari',
    2: 'februari',
    3: 'maret',
    4: 'april',
    5: 'mei',
    6: 'juni',
    7: 'juli',
    8: 'agustus',
    9: 'september',
    10: 'oktober',
    11: 'november',
    12: 'desember'
}

romawi = {
    'I': 1,
    'V': 5,
    'X': 10,
}

waktu_id = {
        'WIB' : 'waktu indonesia barat',
        'WITA': 'waktu indonesia tengah',
        'WIT' : 'waktu indonesia timur'
        }


def get_numerical_sentences(sentences, nsamples=None):
    """
    Get sentences containing numbers [0-9] from corpus
    """
    is_num_sent = list(map(re_num.search, iter(sentences)))
    num_sent = [sentences[i] for i in range(len(sentences)) if is_num_sent[i]]

    if not nsamples:
        return num_sent
    else:
        samples = random.sample(range(len(num_sent)), nsamples)
        return [num_sent[i] for i in samples]

def replace_tb(context):
    context = context.lower()
    temp = context.replace(",", "")
    temp = temp.replace(".", "")
    temp = temp.replace("!", "")
    temp = temp.replace("?", "")
    temp = temp.replace("(", "")
    temp = temp.replace(")", "")

    return temp

def parse_dash(sentence):
    """
    Parse dashes in sentence into words.
    Parameters: sentence: string
                A sentence that might or might not contain dash(es).
    Returns:    parsed_sentence: string
                New sentence in which the dashes are replaced with a word.
                If the parameter sentence does not contain any dash, original
                sentence is returned.
    """
    # print(sentence)
    sentence = sentence.replace("--", '')
    sentence = re.sub('-+', '-', sentence)
    # sentence = sentence.replace("- ", '')
    # sentence = sentence.replace(" -", '')

    matches = re_dash.findall(sentence)
    # print("matches: {}\nsentence: {}".format(matches, sentence))
    if not matches:
        # sentence = sentence.replace("--", '')
        # sentence = sentence.replace("- ", '')
        # print(sentence)
        return sentence

    # sentence = sentence.replace(" - ", '')
    # print("{} {}".format(matches,sentence))

    context = re_dash.split(sentence)
    sentence_ = ''

    #print(context)
    # print(sentence)

    for i, match in enumerate(matches):
        sentence_ += context[i]
        if context[i] != "" and context[i+1] != "":
            # print("cont " + context[i] + " " + context[i+1])
            # print("if {} {}".format(context[i].split()[-1], context[i+1].split()[0]))
            if context[i][-1] == 'H' and context[i+1][0] in string.digits:
                #print("ASDF")
                sentence_ += match.replace('-', ' min ')
            elif context[i+1][0] in string.digits \
                    and (context[i][-1] in string.digits \
                        or context[i].split()[-1] in ['dolar', 'amerika',\
                            'rupiah']):
                # print("JKL;")
                sentence_ += match.replace('-', ' hingga ')
            else:
                left_cont = replace_tb(context[i].split()[-1])
                right_cont = replace_tb(context[i+1].split()[0])
                if (left_cont == right_cont):
                    print("if {} {}".format(left_cont, right_cont))
                    #print("HAYOLO")
                    sentence_ += match.replace('-', ' ')
                else:
                    print("else {} {}".format(left_cont, right_cont))
                    sentence_ += match.replace('-', '-')

    return sentence_ + context[-1]


def parse_plus(sentence):
    matches = re.findall(r'\+', sentence)
    if not matches:
        return sentence
    context = re.split(r'\+', sentence)
    sentence_ = ''

    for i, match in enumerate(matches):
        sentence_ += context[i]
        sentence_ += match.replace('+', ' ples ')
    
    return sentence_ + context[-1]


def strip_dash(sentence):
    """
    Remove dash in the sentence
    """
    return sentence.replace('-', ' ')


def parse_degree(sentence):
    degs = re_degree.findall(sentence)
    if not degs:
        return sentence

    context = re_degree.split(sentence)
    sentence_ = ''

    for i, d in enumerate(degs):
        sentence_ += context[i]
        sentence_ += degree[d]

    sentence_ += context[-1]
    return sentence_


def parse_numerals(sentence):
    """
    Parse numerals in sentence into words.
    Parameters: sentence: string
                A sentence that might or might not contain numeral(s).
    Returns:    parsed_sentence: string
                New sentence in which numerals are replaced with corresponding words.
                If the parameter sentence does not contain any numeral, original
                sentence is returned.
    """
    numerals = re_form.findall(sentence)
    if not numerals:
        return sentence
    # print(numerals)

    context = re_form.split(sentence)
    sentence_ = ''

    for i, num in enumerate(numerals):
        # print('\n')
        # print((i, num))
        # Check context surrounding numeral
        left_context = context[i].strip().split()
        if left_context:
            left = left_context[-1].lower()
        else:
            left = ''
        right_context = context[i + 1].strip().split()
        if right_context:
            right = strip_punct_all(right_context[0]).lower()
        else:
            right = ''
        sentence_ += context[i]
        # print(left)
        # print(right)
    
        # This assumes separators exist between AT MOST TWO NUMBERS
        m = re_sep.search(num)
        if m:
            # print(m)
            # If separator is at the beginning or end something's wrong
            if m.span()[0] == 0 or m.span()[-1] == len(num):
                # print(m.span())
                # print(str(1))
                # Strip punctuation from numeral and read as ordinary number
                sentence_ += numeral_to_word_seq(num.translate(str.maketrans(
                    {k: None for k in string.punctuation})))
            elif m.group(0) == '-':
                # print(str(2))
                s1, s2 = num.split('-')
                # score comparison
                if left in ['unggul'] or right in ['atas']:
                    sentence_ += numeral_to_word_seq(s1) + \
                        ' ' + numeral_to_word_seq(s2)
                else:
                    #print(sentence, s1, s2)
                    sentence_ += numeral_to_word_seq(s1) + \
                        ' sampai ' + numeral_to_word_seq(s2)
            elif m.group(0) == '.':
                # print(str(3))
                # waktu
                if left in ['pukul', 'jam'] or right in ['wib', 'wita', 'wit']:
                    #print(left)
                    #print(right)
                    #print("left in pukul/jam " + str(left in ['pukul','jam']))
                    #print("right in WIB/WITA/WIT " + str(right in ['wib', 'wita',\
                    #    'wit']))
                    parts = re.split(r'[\.:]', num)
                    jam = parts[0]
                    menit = parts[1]
                    #print((jam, menit))
                    jam = str(int(jam))
                    #if menit == '00':
                    #    sentence_ += numeral_to_word_seq(str(int(jam)))
                    #else:
                    #    sentence_ += numeral_to_word_seq(jam) + \
                    #        ' ' + numeral_to_word_seq(menit)
                    sentence_ += numeral_to_word_seq(jam) + \
                            ' ' + numeral_to_word_seq(menit)
                else:
                    if ',' in num:
                        s1, s2 = num.split(',')
                        sentence_ += numeral_to_word_seq(s1.replace('.', '')) + " koma " + numeral_to_word_seq(s2)
                    else:
                        sentence_ += numeral_to_word_seq(num.replace('.', ''))
            elif m.group(0) == ',':
                # print(str(4))
                s1, s2 = num.split(',')
                # numbers behind coma are pronounced individually
                sentence_ += numeral_to_word_seq(s1) + ' koma ' + ' '.join(
                    [numeral_to_word_seq(n) for n in list(s2)])
        else:
            # print('hayolo')
            sentence_ += ' '+ numeral_to_word_seq(num)
    return sentence_ + context[-1]


def parse_waktu_id(sentence):
    """
    Parse WIB, WITA, WIT into corresponding acronyms.
    """
    tz = re_time_zone.findall(sentence)
    if not tz:
        return sentence
    
    context = re_time_zone.split(sentence)
    sentence_ = ''

    for i, t in enumerate(tz):
        if (t != "WIB") and (t != "WITA") and (t != "WIT"):
            t = "WIB"
        sentence_ += context[i]
        sentence_ += waktu_id[t]

    sentence_ += context[-1]
    return sentence_


def numeral_to_word_seq(num_string):
    """
    Accepts string of numbers only and returns corresponding word sequence
    Parameters: num_string: string
                A string that contains numeral(s).
    Returns:    read_num: string
                A sequence of words corresponding with number i.e how number(s) in
                num_strings would be read in Indonesian.
    """
    # partition into groups of three
    # if '.' in numeral:
    # if numeral.index('.') == 2:
    # numeral = numeral.split('.')[0]
    # print(num_string)
    nlen = len(num_string)
    thous = int((nlen - 1)/3)
    # check if number is very large or starts with 0 (phone number)
    if thous > 5 or num_string.startswith('0'):
        return ' '.join([nomor[n] for n in num_string])
    fill = num_string.zfill((thous + 1) * 3) if nlen % 3 != 0 else num_string

    res = []
    for i, num in enumerate([fill[i:i+3] for i in range(0, len(fill), 3)]):
        n0, n1, n2 = num
        if n0 == '0' and n1 == '0' and n2 == '0':
            continue
        if n0 != '0':
            if n0 == '1':
                res.append('seratus')
            else:
                res.extend([nomor[n0], 'ratus'])
        if n1 != '0':
            if n1 == '1':
                if n2 == '0':
                    res.append('sepuluh')
                elif n2 == '1':
                    res.append('sebelas')
                else:
                    res.extend([nomor[n2], 'belas'])
            else:
                res.extend([nomor[n1], 'puluh'])
        if n2 != '0' and n1 != '1':
            if n2 == '1' and n1 == '0' and n0 == '0' and thous - i == 1:
                res.append('seribu')
                continue
            else:
                if n2 != '.':
                    res.append(nomor[n2])
        if thous - i > 0:
            res.append(base[thous - i])
    return ' '.join(res)


def parse_roman(sentence):
    """
    Parse roman numerals in sentence into words.
    Parameters: sentence: string
                A sentence that might or might not contain roman numeral(s).
    Returns:    parsed_sentence: string
                New sentence in which roman numerals are replaced with 
                corresponding words.
                If the parameter sentence does not contain any roman numeral, original
                sentence is returned.
    """
    romans = re_roman.findall(sentence)
    if not romans:
        return sentence
    cont = re_roman.split(sentence)
    sentence_ = ''
    for i, roman in enumerate(romans):
        sentence_ += cont[i]
        num_list = [romawi[r] for r in roman]
        num_sum = 0
        if len(num_list) > 1:
            for n in range(len(num_list) - 1):
                if num_list[n] < num_list[n + 1]:
                    num_sum += num_list[n + 1] - num_list[n]
                elif num_list[n] >= num_list[n + 1]:
                    num_sum += num_list[n]
            if num_list[len(num_list) - 1] <= num_list[len(num_list) - 2]:
                num_sum += num_list[len(num_list) - 1]
        else:
            num_sum = num_list[0]
        sentence_ += numeral_to_word_seq(str(num_sum))
    return sentence_ + cont[-1]


def parse_dates(sentence):
    """
    Parse dates in sentence into words.
    Parameters: sentence: string
                A sentence that might or might not contain date(s).
    Returns:    parsed_sentence: string
                New sentence in which dates are replaced with corresponding words.
                If the parameter sentence does not contain any date, original
                sentence is returned.
    """
    dates = re_date.findall(sentence)
    #print(dates)
    if not dates:
        return sentence
    cont = re_date.split(sentence)
    sentence_ = ''
    for i, date in enumerate(dates):
        sentence_ += cont[i]
        if date.find('/') > 0:
            tan, bul, tah = date.split('/')
            if int(bul) < 13:
                sentence_ += tan + ' ' + bulan[int(bul)] + ' '
                continue
        sentence_ += ' ' + date
    return sentence_ + cont[-1]


def parse_units(sentence):
    """
    Parse units e.g kg, cm, ml in sentence into words.
    Parameters: sentence: string
                A sentence that might or might not contain unit(s).
    Returns:    parsed_sentence: string
                New sentence in which units are replaced with corresponding words.
                If the parameter sentence does not contain any unit, original
                sentence is returned.
    """
    units_ = re_units.findall(sentence)
    # if len(re_units_last.findall(sentence)) != 0:
    #    units_.append(re_units_last.findall(sentence)[-1])
    if not units_:
        return sentence
    cont = re_units.split(sentence)
    #print(units_ + cont)
    #cont[-1] = re_units_last.split(cont[-1])[0]
    # print(cont)
    sentence_ = ''
    for i, unit in enumerate(units_):
        #print(unit)
        sentence_ += cont[i]
        # print(cont[i])
        # print(unit)
        r = re.compile(r'[a-zA-Z]')
        r_num = re.compile(r'[23]')
        #r_cc = re.compile(r' cc[ ]*')
        # if len(r_cc.findall(unit)) != 0:
        # print(unit)
        #sentence_ += ' ' + 'centimeter kubik '
        if unit == 'cc':
            sentence_ += ' c c '
        else:
            if len(r.findall(unit)) == 1:
                if len(r_num.findall(unit)) == 0:
                    # print(units[unit[1]])
                    sentence_ += units[unit[0]]
                else:
                    sentence_ += units[unit[0]] + ' ' + pow_units[unit[1]]
            elif len(r.findall(unit)) > 1:
                #print("HE: {} {}".format(r_num.findall(unit), unit[0]))
                if len(r_num.findall(unit)) == 0:
                    # print(base_units[unit[1]]+units[unit[2]])
                    #print(base_units[unit[0]])
                    #print(units[''.join(unit[1:])])
                    sentence_ += base_units[unit[0]] + units[''.join(unit[1:])]
                else:
                    sentence_ += base_units[unit[0]] + \
                        units[unit[1]] + ' ' + pow_units[unit[2]]
    if len(units_) == len(cont):
        return sentence_
    else:
        return sentence_ + cont[-1]

def currency_converter(currency_string):
    """
    Accepts string of currency and numbers (e.g $15000, Rp 1 Trilyun) only and 
    returns corresponding word sequence
    Parameters: currency_string: string
                A string that contains number with currency.
    Returns:    read_currency: string
                A sequence of words and numbers corresponding with currency_string.
                currency_converter() does not change numerals in currency_string
                into read numerals, so any numerals will remain intact.
    """
    rc = re.compile('|'.join([r'\bRp', r'\$', r'USD', r'US$', r' ']))
    currs = rc.findall(currency_string)
    currs = [x for x in currs if x != ' ']
    cont = currs + rc.split(currency_string.strip('.'))
    cont = [x for x in cont if x != '']
    #print(cont)
    if len(cont) < 3:
        return cont[1]+' '+currency[cont[0]]
    else:
        return cont[1]+' '+cont[2]+' '+currency[cont[0]]

def parse_currency(sentence):
    """
    Parse currency in sentence into words.
    Parameters: sentence: string
                A sentence that might or might not contain currency(s).
    Returns:    parsed_sentence: string
                New sentence in which currency are replaced with corresponding words.
                If the parameter sentence does not contain any currency, original
                sentence is returned.
    """
    currs = re_curr.findall(sentence)
    #print(currs)
    if not currs:
        return sentence

    cont = re_curr.split(sentence)
    #print(cont)
    sentence_ = ''
    for i, curr in enumerate(currs):
        #print(curr)
        #print(cont[i])
        sentence_ += cont[i] + currency_converter(curr)
    return sentence_ + cont[-1]


def parse_caps(sentence):
    caps = re_caps.findall(sentence)
    # print(caps)
    if not caps:
        return sentence
    
    caps = [count_caps(x) for x in caps]
    # print(caps)
    cont = re_caps.split(sentence)
    sentence_ = ''
    for i, cap in enumerate(caps):
        sentence_ += cont[i]
        if len(cap) > 1:
#            sentence_ += ' ' + '-sP-'.join(list(cap.lower())) + ' '
            sentence_ += '-@-'.join(list(cap.lower()))
        else:
            sentence_ += cap.lower()
    return sentence_ + cont[-1]


def parse_percents(sentence):
    percent = re.findall(r'%', sentence)
    if not percent:
        return sentence

    context = re.split(r'%', sentence)
    sentence_ = ''
    for i, perc in enumerate(percent):
        sentence_ += context[i]
        sentence_ += perc.replace('%', ' persen ')

    return sentence_ + context[-1]


def count_caps(caps):
    cons = re.compile(r'(([A-Z])\2{2,})')
    cons_caps = [x[0] for x in cons.findall(caps)]
    char_caps = [x[1] for x in cons.findall(caps)]
 
    if not cons_caps:
        return caps

    context = cons.split(caps)
    count_caps = ''
    for i, cc in enumerate(cons_caps):
        count_caps += context[i]
        count_caps += char_caps[i] + str(len(cc))

    return count_caps + context[-1]


def parse_internets(sentence):
    internets = re_intr.findall(sentence)
    if not internets:
        return sentence
    context = re_intr.split(sentence)
    sentence_ = ''
    for i, intr in enumerate(internets):
        # print(intr)
        sentence_ += context[i]

        if intr[0] == '#':
            intr = intr.replace('#', 'hashtag ')
        elif intr[0] == '@':
            intr = intr.replace('@', 'et ')
        else:
            if not re_form.match(intr):
                intr = intr.replace('@', ' et ').replace('.', ' dot ')
        
        sentence_ += \
                intr.replace('_', ' anderskor ').replace('/', ' slash ')\
                .replace(':', ' titik dua ')
    
    return sentence_ + context[-1]


def parse_phones(sentence):
    phones = re_phone.findall(sentence)
    if not phones:
        return sentence

    context = re_phone.split(sentence)
    sentence_ = ''

    for i, ph in enumerate(phones):
        sentence_ += context[i]
        ph = ph.replace('(', '').replace(')', '').replace('-', ' ').strip()
        ph = ' '.join([x for x in ph if x != ' '])
        ph = ph.replace('*', ' bintang ').replace('#', ' pagar ')
        sentence_ += ph

    return sentence_ + context[-1]


def parse_parentheses(sentence):
    parnths = re_parnth.findall(sentence)
    # print("parnths: {}".format(parnths))
    if not parnths:
        return sentence

    context = re_parnth.split(sentence)
    # print("context: {}".format(context))
    sentence_ = ''

    for i, par in enumerate(parnths):
        # print(par)
        #print(context)
        left_context = context[i].strip().split()
        if left_context:
            left = left_context[-1].strip()
            # print(left)
            # print(re.search(r'(?<=\()[0-9]+(?=\))', par))
            # print(left[0])
            sentence_ += context[i].strip()
            if left[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                    and re.search(r'(?<=\()[0-9]+(?=\))', par):
                if context[i+1]:
                    if context[i+1][0] in '.,?!':
                        par = ', ' + par[1:-1] + ' tahun'
                    else:
                        par = ', ' + par[1:-1] + ' tahun, '
                sentence_ += par
            elif re.match(r'[Aa]yat', left) and par[1] in string.digits:
                par = ' ' + par.replace('(','').replace(')', '') + ' '
                sentence_ += par
            else:
                # print(context[i+1])
                if context[i+1]:
                    if context[i+1][0] in '.,?!':
                        par = ', ' + par.replace('(', '').replace(')', '')
                    else:
                        par = ', ' + par.replace('(', '').replace(')', '') + ', '
                sentence_ += par
    return sentence_ + context[-1]


def parse_slash(sentence):
    slash = re.findall(r'\/', sentence)
    if not slash:
        return sentence

    context = re.split(r'\/', sentence)
    sentence_ = ''
    uu_flag = False

    for i, sls, in enumerate(slash):
        # print('HAI: '+context[i])
        sentence_ += context[i].strip()
        left_context = context[i].strip().split()
        if left_context:
            if "nomor" in left_context or "Nomor" in left_context:
                uu_flag = True

            if uu_flag == True:
                sls = sls.replace('/', ' garis miring ')
            else:
                sls = sls.replace('/', ' atau ')
        else:
            sls = sls.replace('/', ' slash ')
        sentence_ += sls

    return sentence_ + context[-1]

def strip_punctuation(sentence):
    punct = ''.join([x for x in string.punctuation if x not in '!?,.+-/$%&_@#'])
    return sentence.translate(
        str.maketrans({k: '' for k in punct}))


def strip_punct_all(sentence):
    return sentence.translate(str.maketrans({k: '' for k in string.punctuation}))


def strip_period(sentence):
    if sentence.endswith('.'):
        return sentence[:-1]
    else:
        return sentence


def strip_whitespace(sentence):
    return ' '.join(sentence.split())


def strip_quotes(sentence):
    return sentence.replace('\"', '')


def strip_unicode(sentence):
    return sentence.encode('ascii', errors='ignore').decode()


def add_pause(sentence):
    return sentence.replace(' ', ' P ')


def add_short_pause(sentence):
    return sentence.replace('@', 'S')


def lower_caps(sentence):
    return sentence.lower()


def edit_pronunciations(sentence):
    words = open('lex_tts_final').read().split('\n')
    dct = {}
    for x in words[:-1]:
        dct[x.split()[0]] = x.split()[1]

    for x in dct.keys():
        pat = re.compile(r'\b%s\b' % x, re.I)
        sentence = re.sub(pat, dct[x], sentence)
        #sentence.replace(x, dct[x])
    
    return sentence


def preprocess(sentence, pipeline=None):
    """
    Accepts an input sentence and a pipeline containing a list of functions to
    apply sequentially to the input sentence.
    """
    if not pipeline:
        pipeline = [parse_dash,
                    strip_quotes, 
                    strip_unicode, 
                    parse_dates,
                    parse_currency, 
                    parse_phones, 
                    parse_parentheses,
                    parse_internets,
                    parse_units, 
                    parse_plus, 
                    parse_roman,
                    strip_whitespace, 
                    parse_numerals, 
                    parse_waktu_id,
                    strip_whitespace, 
                    lower_caps, 
                    parse_numerals, 
                    parse_percents, 
                    parse_slash,
                    strip_punctuation, 
                    strip_whitespace
                    ]
                    # strip_dash,
                    # strip_dash
                    # parse_caps, 
                    # edit_pronunciations, 
                    # add_short_pause,
                    # add_pause,

    for fn in pipeline:
        sentence = fn(sentence)
    return sentence


def preprocess_batch(sentences, pipeline=None):
    """
    Accepts a list of sentences and a pipeline containing a list of
    functions to apply sequentially on each sentence.
    Parameters: sentences: list
                A list of sentences that contains symbols, numerals, etc. that need
                to be converted into words.
                pipeline: list, optional
                A list of functions to apply on sentences. If no pipeline is passed,
                this function will used default pipeline that contains all parsing
                functions available in this module.
    Returns:    parsed_sentences: list
                A list of parsed sentences.
    """
    if not pipeline:
        pipeline = [
                    parse_dash,
                    strip_quotes, 
                    strip_unicode, 
                    parse_dates,
                    parse_currency, 
                    parse_phones, 
                    parse_parentheses,
                    parse_internets,
                    parse_units, 
                    parse_plus, 
                    parse_roman,
                    strip_whitespace, 
                    parse_numerals, 
                    parse_waktu_id,
                    strip_whitespace, 
                    lower_caps, 
                    parse_numerals, 
                    parse_percents, 
                    parse_slash,
                    strip_punctuation, 
                    strip_whitespace
                    ]
                    # strip_dash,
                    # strip_dash
                    # strip_quotes, 
                    # strip_unicode, 
                    # parse_dates,
                    # parse_currency, 
                    # parse_phones, 
                    # parse_parentheses,
                    # parse_internets,
                    # parse_units, 
                    # parse_plus, 
                    # parse_roman,
                    # strip_whitespace, 
                    # parse_numerals, 
                    # parse_waktu_id,
                    # strip_whitespace, 
                    # lower_caps, 
                    # parse_numerals, 
                    # parse_percents, 
                    # parse_slash,
                    # strip_punctuation, 
                    # strip_whitespace
                    # parse_caps, 
                    # edit_pronunciations, 
                    # add_short_pause,
                    # add_pause,

    sentences_ = []
    for sentence in sentences:
        # print("pre: {}".format(sentence))
        #print(sentence)
        sentence = sentence.replace('?', ' ')
        sentence = sentence.replace('!', ' ')
        sentence = sentence.replace('- ', '-')
        for fn in pipeline:
            sentence = fn(sentence)
        sentence = sentence.replace(',', ' ')
        sentence = sentence.replace('.', ' ')
        sentence = sentence.replace('&amp', ' ')
        sentence = re.sub(' +', ' ', sentence)
        sentence = sentence.replace('- ', ' ')
        sentences_.append(sentence)

    return sentences_


if __name__ == '__main__':
    parser = ArgumentParser(description='Provides tools for cleaning and \
            parsing text.')
    parser.add_argument('--input', type=str, help='Path to input file.')
    parser.add_argument('--output', type=str, help='Path to output file.')
    parser.add_argument('--nthreads', type=int, default=None,
                        help='Number of threads to use.')
    args = parser.parse_args()

    try:
        sentences = open(args.input, encoding='utf8').read().splitlines()
    except Exception as e:
        sys.exit(e)

    if args.nthreads != None:
        nchunk = int(len(sentences) / (args.nthreads * 2))
        chunks = [[sentences[i:i + nchunk]]
                  for i in range(0, len(sentences), nchunk)]

        with Pool(args.nthreads) as pool:
            parsed = pool.starmap(preprocess_batch, chunks)
        with open(args.output, 'w') as f:
            for p in parsed:
                for s in p:
                    f.write(s + '\n')
    else:
        parsed = preprocess_batch(sentences)
        with open(args.output, 'w') as f:
            for p in parsed:
                f.write(p + '\n')
