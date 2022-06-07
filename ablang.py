class Context:
    def __init__(self, s, funcDescrip=None):
        self.data = s
        self.end = False
        self.fd = funcDescrip

    def setData(self, new, rule, verbose=False):
        if verbose:
            print('\t', rule)
        self.data = new
        if verbose:
            print(self)

    def __repr__(self):
        s = self.data
        if self.fd:
            s += f' ({self.fd(self.data)})'
        return s


class Rule:
    KW1_POOL = (None, 'once', 'start', 'end')
    KW2_POOL = (None, 'return', 'start', 'end')

    def __init__(self, w1, w2, kw1=None, kw2=None):
        self.w1 = w1
        self.w2 = w2
        self.kw1 = kw1
        self.kw2 = kw2
        self.end = False

    def execute(self, ctx, verbose=True):
        if self.end or ctx.end:
            return False

        data = ctx.data
        # find index
        try:
            if self.kw1 == 'start':
                assert data.startswith(self.w1)
                idx = 0
            elif self.kw1 == 'end':
                assert data.endswith(self.w1)
                idx = len(data) - len(self.w1)
            else:
                idx = data.index(self.w1)
        except:
            return False

        # replace
        sl, sr = data[:idx], data[idx + len(self.w1):]
        if self.kw2 == 'start':
            data = self.w2 + sl + sr
        elif self.kw2 == 'end':
            data = sl + sr + self.w2
        elif self.kw2 == 'return':
            data = self.w2
        else:
            data = sl + self.w2 + sr
        ctx.setData(data, self, verbose)
        if self.kw2 == 'return':
            ctx.end = True
        if self.kw1 == 'once':
            self.end = True

        return True

    def __repr__(self):
        ls, rs = self.w1, self.w2
        if self.kw1:
            ls = f'({self.kw1}){ls}'
        if self.kw2:
            rs = f'({self.kw2}){rs}'
        res = ls + '=' + rs
        if self.end:
            res = '# ' + res
        if hasattr(self, 'idx'):
            res = f'{self.idx}. {res}'
        return res

    @classmethod
    def subparse(cls, part):
        try:
            assert 0 <= part.count('(') == part.count(')') <= 1
        except:
            raise ValueError('wrong parentheses', part)
        if '(' not in part:
            return None, part
        try:
            assert part[0] == '('
            return part[1:].split(')', 1)
        except:
            raise ValueError('wrong parentheses', part)

    @classmethod
    def parse(cls, line):
        line = line.replace(' ', '')
        if not line:
            return None
        if '#' in line:
            raise ValueError('no comment here', line)
        if line.count('=') != 1:
            raise ValueError('mismatched "=" count', line)

        p1, p2 = line.split('=')
        k1, w1 = cls.subparse(p1)
        if k1 not in cls.KW1_POOL:
            raise ValueError(f'invalid keyword: {k1}', p1)
        k2, w2 = cls.subparse(p2)
        if k2 not in cls.KW2_POOL:
            raise ValueError(f'invalid keyword: {k2}', p2)

        return cls(w1, w2, k1, k2)


class RuleSet:
    def __init__(self, code):
        lines = []
        for i, line in enumerate(code.split('\n')):
            if '#' in line:
                line = line.split('#', 1)[0]
            try:
                rule = Rule.parse(line)
            except:
                print('error at line', i)
                raise
            if rule:
                lines.append(rule)

        self.code = lines
        for i, r in enumerate(self.code):
            r.idx = i

    def _executeOnce(self, ctx, verbose):
        return any(r.execute(ctx, verbose) for r in self.code)

    def execute(self, data, verbose=False, limit=100000):
        if isinstance(data, str):
            data = Context(data)

        if verbose:
            print(data)

        loop = 0
        while self._executeOnce(data, verbose):
            loop += 1
            if loop >= limit:
                raise RuntimeError('time limit exceeded')

        return data.data

    def __repr__(self):
        return '\n'.join(map(str, self.code))


if __name__ == '__main__':
    subrule = RuleSet('''
    (start)ooonnn=(end)C
    (start)true=(end)-true-
    (start)oonn=(end)B
    (start)on=(end)A
    (start)no=(end)'
    ''')

    def descrip(s):
        return subrule.execute(s, False)

    rs = RuleSet('''
    aa=ononnoa
    ab=ononnob
    ac=ononnoc
    oa=oononno
    b=oonnoonnno
    c=ooonnnooonnnno
    noono=onnoo
    nooonno=oonnnoo
    noooonnno=ooonnnnoo
    ononno=true
    oonnoonnno=true
    ooonnnooonnnno=true
    trueo=o
    on=
    no=false''')
    c = Context('abba', descrip)

    print('Rules:')
    print(rs, '\n')

    print('Input:')
    print(c, '\n')

    print('Run:')
    rs.execute(c, True)
