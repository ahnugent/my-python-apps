# script:   complexmath.py
# author:   Allen H nugent
# date:     2017-05-18
#
# description:  A calculator for complex numbers.
#
# TODO: support 'a + i b' notation


import math

class Cvector:
    def __init__(self, a=0, b=0):
        self.a = a
        self.b = b
    def real(self):
        return self.a
    def imag(self):
        return self.b
    def modulus(self):
        return math.sqrt(self.a **2 + self.b **2)
    def phase(self):
        if self.b == 0:
            return 0
        else:
            return math.atan2(self.b, self.a)
    def type(self):
        return 'vector'

class Cphasor:
    def __init__(self, r=0, p=0):
        self.r = r
        self.p = p
    def real(self):
        return (self.r * math.cos(self.p))
    def imag(self):
        return (self.r * math.sin(self.p))
    def modulus(self):
        return self.r
    def phase(self):
        return self.p
    def type(self):
        return 'phasor'

def PhasorToVector(p):
    v = Cvector()
    v.a = p.real()     # p.a = real part
    v.b = p.imag()     # p.b = imaginary part
    return v

def VectorToPhasor(v):
    p = Cphasor()
    p.r = v.modulus()
    p.p = v.phase()
    return p

# this was only used during early dev:
def parseReal(s):
    ic = s.find(',')
    print "ic = %d"% (ic)
    if ic >= 0:
        print "s[0:1] = %s"% (s[0:1])
        sreal = s[0:ic]
        print "C: sreal = %s"% (sreal)
    else:
        sreal = s
        print "R: sreal = %s" % (sreal)
    return float(s)

def parseComplex(s):
    s = s.strip()
    s = s.strip('(')
    s = s.strip(')')

    ii = s.find('i')
    if ii >= 0:  # using standard 'a + iB' notation
        sign2 = s[ii - 1]
        imult2 = signToNum(sign2)
        # TODO: if imult2 == 0 PROBLEM
        sign1 = s[0]
        imult1 = signToNum(sign1)
        if (imult1 == 0):
            imult1 = 1
            sreal = s[0:(ii - 1)]
        else:
            sreal = s[1:(ii - 1)]
        simag = s[(ii + 1):]
        v = Cvector(float(sreal) * imult1, float(simag) * imult2)
        # v.a = float(sreal) * imult1
        # v.b = float(simag) * imult2
    else:
        ic = s.find(',')
        if ic >= 0:  # a dyad was entered
            ia = s.find('@')
            if ia >= 0:  # using (magnitude, phase) representation
                smagn = s[0:ic]
                sphase = s[ia + 1:]
                v = Cphasor(float(smagn), float(sphase))
                # v.r = float(smagn)
                # v.p = float(sphase)
                #v = PhasorToPoint(float(smagn), float(sphase))
            else:        # using (real, imaginary) representation
                sreal = s[0:ic]
                simag = s[ic + 1:]
                v = Cvector(float(sreal), float(simag))
                # v.a = float(sreal)
                # v.b = float(simag)
        else:  # a monad was entered: assume the number has no imaginary part
            sreal = s
            simag = 0
            v = Cvector(float(sreal), float(simag))
            # v.a = float(sreal)
            # v.b = float(simag)
    return v

def signToNum(sign):
    if sign == '+':
        mult = 1
    else:
        if sign == '-':
            mult = -1
        else:
            mult = 0  # no sign; caller must handle default to +1
    return mult

def parseOp(s):
    op = ''
    if s[0] in ops:
        op = s[0]
    return op

def operate(c1, op, c2):
    usephasors = (c1.type() == 'phasor')

    # default to vector arithmetic if mixed types were entered (ignore for monadic operations):
    if op not in ('|', '@'):
        #X: if type(c2).__name__ == 'Cphasor':
        if c1.type() == 'vector' and c2.type() == 'phasor':
            c2 = PhasorToVector(c2)
            usephasors = False
        #TODO: support a+ib in mixed formats

    if usephasors:
        c3 = Cphasor()
    else:
        c3 = Cvector()

    # unary operations returns a monad ...
    if op == '|':  
        c3.a = c1.modulus()
        c3.b = 'nan'
    elif op == '@':
        c3.a = c1.phase()
        c3.b = 'nan'
    # binary operations return a dyad ...
    elif op in ('+', '-'):  
        if usephasors:   # no simple phasor method for addition, so convert to vector
            c1 = PhasorToVector(c1)
            c2 = PhasorToVector(c2)
            c3 = Cvector()
        if op == '+': 
            c3.a = c1.a + c2.a
            c3.b = c1.b + c2.b
        else:
            c3.a = c1.a - c2.a
            c3.b = c1.b - c2.b
        if usephasors:    # convert back
            c3 = VectorToPhasor(c3)
    elif op == '*':
        if usephasors:
            c3.r = c1.r * c2.r
            c3.p = c1.p + c2.p
        else:
            c3.a = c1.a * c2.a - c1.b * c2.b
            c3.b = c1.a * c2.b - c2.a - c1.b
    elif op == '/':
        if usephasors: 
            if c2.r == 0:
                c3.r = 'nan'
                c3.p = 'nan'
            else:
                c3.r = c1.r / c2.r
                c3.p = c1.p - c2.p
        else:
            if c2.modulus == 0:
                c3.a = 'nan'
                c3.b = 'nan'
            else:
                denom = (c2.a ** 2 + c2.b ** 2)
                c3.a = (c1.a * c2.a + c1.b * c2.b) / denom
                c3.b = (c2.a * c1.b - c1.a * c2.b) / denom
    elif op == '^':
        # TODO: how to encode power into kbd input syntax? parse fractional exponent?
        if not usephasors:
            p1 = VectorToPhasor(c1)
            exp = c2.a
        else:
            exp = c2.r
        c3.r = p1.r ** exp
        c3.p = p1.r / exp
        if not usephasors:
            c3 = PhasorToVector(c3)

    return c3, usephasors

# symbols for defined operations:
ops = ('+', '-', '*', '/', '|', '@')
# TODO: create a lookup incl. words 'addition',... 'modulus', 'phase'

formatC = "(%d %s%d)"
formatA = "(%d%s%d)"
formatV = "(%d,%d)"

doStackOutput = False;

#print("Enter a complex number as (a, b) or (r, @p):")
prompt0 = ('Data entry, display formats: \n'
            + 'a = real part, b = imaginary part; r = modulus, p = phase (radians); \n'
            + 'parentheses and spaces are optional. \n\n'
            + 'Enter a complex number as a+ib, (a,b), or (r,@p): ')
prompt1 = 'Enter a complex number as a+ib, (a,b), or (r,@p), or ? for help: '
prompt2 = 'Enter an operation and (optionally) another complex number in the same format: '

s1 = raw_input(prompt0)
# if s1 == '?':
#     prompt = ('a = real part, b = imaginary part; r = modulus, p = phase (radians); \n'
#             + 'parentheses and spaces are optional.')
#     s1 = raw_input(prompt)

while len(s1) != 0:
    v1 = parseComplex(s1)
    complexformat = (s1.find('i') >= 0)
    s2 = raw_input(prompt2)
    op = parseOp(s2)
    if op in ops:
        if op in ('|', '@'):
            v2 = Cvector()   # not needed, so set dummy = (0,0)
        else:
            v2 = parseComplex(s2[1:])  # what happens if no v2?

        v3, usephasors = operate(v1, op, v2)

        if op in ('|', '@'):
            print formatV % (v1.a, v1.b)
            print (op)
            print " = "
            print v3.a
        else:
            if complexformat:      # use complex notation
                if doStackOutput:
                    print formatC % (v1.a, (' ' + (v1.b / abs(v1.b)) + 'i '), v1.b)
                    print (op)
                    print formatC % (v2.a, (' ' + (v2.b / abs(v2.b)) + 'i '), v2.b)
                    print ' = '
                    print formatC % (v3.a, (' ' + (v3.b / abs(v3.b)) + 'i '), v3.b)
                else:
                    print (formatC % (v1.a, (' ' + (v1.b / abs(v1.b)) + 'i '), v1.b) + ' ' + op + ' '
                        + formatC % (v2.a, (' ' + (v2.b / abs(v2.b)) + 'i '), v2.b) + ' = '
                        + formatC % (v3.a, (' ' + (v3.b / abs(v3.b)) + 'i '), v3.b))
            elif usephasors:       # use phasor notation
                if doStackOutput:
                    print formatA % (v1.modulus(), ' @ ', v1.phase())
                    print (op)
                    print formatA % (v2.modulus(), ' @ ', v2.phase())
                    print " = "
                    print formatA % (v3.modulus(), ' @ ', v3.phase())
                else:
                    print (formatA % (v1.modulus(), ' @ ', v1.phase()) + ' ' + op + ' '
                        + formatA % (v2.modulus(), ' @ ', v2.phase()) + ' = '
                        + formatA % (v3.modulus(), ' @ ', v3.phase()))
            else:                  # use vector notation
                if doStackOutput:
                    print formatV % (v1.a, v1.b)
                    print (op)
                    print formatV % (v2.a, v2.b)
                    print ' = '
                    print formatV % (v3.a, v3.b)
                else:
                    print (formatV % (v1.a, v1.b) + ' ' + op + ' '
                        + formatV % (v2.a, v2.b) + ' = '
                        + formatV % (v3.a, v3.b))

    s1 = raw_input(prompt1)

exit(0)
