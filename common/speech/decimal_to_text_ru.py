import decimal
import string
import re
from russian_numerals import prepare

units = (
    u'ноль',

    (u'один', u'одна'),
    (u'два', u'две'),

    u'три', u'четыре', u'пять',
    u'шесть', u'семь', u'восемь', u'девять'
)

teens = (
    u'десять', u'одиннадцать',
    u'двенадцать', u'тринадцать',
    u'четырнадцать', u'пятнадцать',
    u'шестнадцать', u'семнадцать',
    u'восемнадцать', u'девятнадцать'
)

tens = (
    teens,
    u'двадцать', u'тридцать',
    u'сорок', u'пятьдесят',
    u'шестьдесят', u'семьдесят',
    u'восемьдесят', u'девяносто'
)

hundreds = (
    u'сто', u'двести',
    u'триста', u'четыреста',
    u'пятьсот', u'шестьсот',
    u'семьсот', u'восемьсот',
    u'девятьсот'
)

orders = (# plural forms and gender
    #((u'', u'', u''), 'm'), # ((u'рубль', u'рубля', u'рублей'), 'm'), # ((u'копейка', u'копейки', u'копеек'), 'f')
    ((u'тысяча', u'тысячи', u'тысяч'), 'f'),
    ((u'миллион', u'миллиона', u'миллионов'), 'm'),
    ((u'миллиард', u'миллиарда', u'миллиардов'), 'm'),
)

fractional = (
    u'десятых', u'сотых',
    u'тысячных', u'десятитысячных',
    u'стотысячных', u'милионных',
    u'десятимилионных', u'стомилионных',
    u'тысямилионных', u'миллиардных'
)

minus = u'минус'

def thousand(rest, sex):
    """Converts numbers from 19 to 999"""
    prev = 0
    plural = 2
    name = []
    use_teens = rest % 100 >= 10 and rest % 100 <= 19
    if not use_teens:
        data = ((units, 10), (tens, 100), (hundreds, 1000))
    else:
        data = ((teens, 10), (hundreds, 1000))
    for names, x in data:
        cur = int(((rest - prev) % x) * 10 / x)
        prev = rest % x
        if x == 10 and use_teens:
            plural = 2
            name.append(teens[cur])
        elif cur == 0:
            continue
        elif x == 10:
            name_ = names[cur]
            if isinstance(name_, tuple):
                name_ = name_[0 if sex == 'm' else 1]
            name.append(name_)
            if cur >= 2 and cur <= 4:
                plural = 1
            elif cur == 1:
                plural = 0
            else:
                plural = 2
        else:
            name.append(names[cur-1])
    return plural, name


def num2text(num, main_units=((u'', u'', u''), 'm')):
    """
    http://ru.wikipedia.org/wiki/Gettext#.D0.9C.D0.BD.D0.BE.D0.B6.D0.B5.D1.81.
    D1.82.D0.B2.D0.B5.D0.BD.D0.BD.D1.8B.D0.B5_.D1.87.D0.B8.D1.81.D0.BB.D0.B0_2
    """

    _orders = (main_units,) + orders
    if num == 0:
        return ' '.join((units[0], _orders[0][0][2])).strip() # ноль

    rest = abs(num)
    ord = 0
    name = []
    while rest > 0:
        plural, nme = thousand(rest % 1000, _orders[ord][1])
        if nme or ord == 0:
            name.append(_orders[ord][0][plural])
        name += nme
        rest = int(rest / 1000)
        ord += 1
    if num < 0:
        name.append(minus)
    name.reverse()
    return ' '.join(name).strip()

def get_value_int_fract(value):
    value_str=str(value)
    if '.' in value_str:
        integral, exp = str(value).split('.')
    else:
        integral=value
        exp=""
    return integral, exp

def decimal2text(value, places=None,
                 int_units=(('', '', ''), 'm'),
                 exp_units=(('', '', ''), 'm')):
    """ convert numbers in string to words """
    dec_value = decimal.Decimal(value)

    integral, exp=get_value_int_fract(value)
    if len(integral)>10 or len(exp)>10 :
        return prepare(value)

    if places:
        #need quanitze
        q = decimal.Decimal(10) ** -places
        dec_value = dec_value.quantize(q)

    integral, exp=get_value_int_fract(dec_value)

    exp_len=len(exp)
    if exp_len > 0:
        #there is fraction part
        if exp_len <= len(fractional):
            return u'{} целых {} {}'.format(
                num2text(int(integral), int_units),
                num2text(int(exp), exp_units),
                fractional[exp_len-1])
        else:
            return u'{} целых и {}'.format(
                num2text(int(integral), int_units),
                num2text(int(exp), exp_units))
    else:
        return u'{}'.format(
            num2text(int(integral), int_units))

def is_digit(s):
    if not s[0].isnumeric():
        return False

    if s.count('.') + s.count(',') > 1:
        return False

    for ch in s:
        if ch not in string.digits and ch != '.' and ch != ',':
            return False
    return True

def text_num_split(item):
    groups = []
    newword = ""
    digit_found=False
    for index, letter in enumerate(item, 0):
        if is_digit(newword+letter):
            if not digit_found:
                if newword: groups.append(newword)
                newword=""
                digit_found=True
        else:
            if digit_found:
                if newword: groups.append(newword)
                newword=""
                digit_found=False
        newword += letter
    if newword: groups.append(newword)
    return groups

def replace_numbers(text:str)->str:
    """ replace numbers in string with words """
    words=text.split()
    res=""
    for word in words:
        subwords=text_num_split(word)
        if not subwords: continue

        for subword in subwords:
            if is_digit(subword):
                res+=decimal2text(subword)
            else:
                res+=subword
            res+=" "
    return res