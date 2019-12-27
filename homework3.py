import copy
import sys
import time
def eliminate_implication(s):
    stack = s.split('=>')
    if '& 'not in stack[0]:
        for i in range(2):
            stack[i] = stack[i].strip()
        if '~' in stack[0]:
            stack[0]=stack[0][1:]
        else:
            stack[0]='~'+stack[0]
        res = ' | '.join(stack)
    else:
        AndStack=stack[0].split('&')
        for i in range(len(AndStack)):
            AndStack[i]=AndStack[i].strip()
            if AndStack[i][0]=='~':
                AndStack[i]=AndStack[i][1:]
            else:
                AndStack[i]='~'+AndStack[i]
        AndStack.append(stack[1].strip())
        res = ' | '.join(AndStack)
    return res
def CNF(s):
    if '=>' in s:
        line = eliminate_implication(s)
    elif '&' in s:
        AndStack=s.split('&')
        for i in range(len(AndStack)):
            AndStack[i]=AndStack[i].strip()
            if AndStack[i][0]=='~':
                AndStack[i]=AndStack[i][1:]
            else:
                AndStack[i]='~'+AndStack[i]
        line = ' | '.join(AndStack)
    else:
        if s[0] ==' ~':
            line = s[1:]
        else:
            line = s
    return line
def isVariable(s):
    if isinstance(s, str):
        if s.islower():
            return True
def isPredicate(predicate):
    if isinstance(predicate, list):
        if len(predicate) > 2:
            if not predicate[1][0].islower():
                if predicate[0] == '' or predicate[0] == '~':
                    return True
    return False
def parse(s):
    c = statements()
    a = s.split('|')
    for index in range(len(a)):
        a[index] = a[index].strip(' ')
    for clau in a:
        pred = predicate(clau)
        c.add(pred)
    c.sort()
    return c
def predicate(sss):
    pred=[]
    for i in range(3):
        pred.append('')
    a = sss.split('(')
    if a[0][0] == '~':
        pred[0] = a[0][0]
        pred[1] = a[0][1:]
    else:
        pred[0] = ''
        pred[1] = a[0]
    aa = a[1].split(')')
    aaa = aa[0].split(',')
    pred[2:] = aaa
    return pred

class statements:
    def __init__(self, listP = None):
        self.predicates = []
        if listP:
            for i in listP:
                self.predicates.append(i)

    def norm(self, idx=1):
        count = {}
        for p in self.predicates:
            l = len(p)
            for i in range(2, l):
                if isVariable(p[i]) and p[i] not in count:
                    count[p[i]] = str(idx)
                    idx += 1
        for p in self.predicates:
            l = len(p)
            for i in range(2, l):
                if isVariable(p[i]):
                    p[i] = 'x' + count[p[i]]
        return idx

    def add(self, p):
        self.predicates.append(p)

    def sort(self):
        self.predicates.sort()

    def ToStr(self):
        return str(self.predicates)

    def AS(self, subst):
        for p in self.predicates:
            for i in range(2, len(p)):
                key = p[i]
                if key not in subst:
                    continue
                else:
                    while subst[key] in subst:
                        key = subst[key]
                    p[i] = subst[key]
        s = set()
        temp = []
        for p in self.predicates:
            if str(p) not in s:
                temp.append(p)
                s.add(str(p))

        self.predicates = temp

class KB:
    def __init__(self):
        self.clauses = []
        self.kBS = set()

    def input(self, s):
        c = parse(s)
        c.norm()
        self.clauses.append(c)
        self.kBS.add(c.ToStr())

def resolve(c1, c2):
    for a in c1.predicates:
        for b in c2.predicates:
            if a[0] != b[0] and a[1] == b[1]:
                return True
    return False

def standardA(clause1, clause2):
    clause2.norm(clause1.norm() + 1)

def add_set(sett,a,v):
    s = sett.copy()
    s[a] = v
    return s

def unifyVar(x, y, sub):
    if x in sub:
        return unify(sub[x], y, sub)
    elif y in sub:
        return unify(x, sub[y], sub)
    else:
        return add_set(sub, x, y)

def split_or(s):
    if '|' in s:
        res = s.split('|')
    else:
        res = [s]
    return res



def unify(x, y, z):
    if z == None:
        return None
    elif x == y:
        return z
    elif isVariable(x):
        return unifyVar(x, y, z)
    elif isVariable(y):
        return unifyVar(y, x, z)
    elif isPredicate(x) and isPredicate(y):
        return unify(x[2:], y[2:], z)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        return unify(x[1:], y[1:], unify(x[0], y[0], z))
    else:
        return None

def find_predicate_and_arguments(s):
    stack = s.split('(')
    predicate = stack[0]
    l = stack[1].split(')')
    if ',' in l[0]:
        ans = l[0].split(',')
    else:
        ans = [l[0]]
    return predicate, ans




def resolveTwo(p):
    clause1 = p[0]
    clause2 = p[1]
    ans = []
    c1 = clause1.predicates
    c2 = clause2.predicates
    for p1 in c1:
        for p2 in c2:
            if ((p1[0] == '' and p2[0] == '~') or (p1[0] == '~' and p2[0] == '')) and p1[1] == p2[1]:
                i1 = c1.index(p1)
                i2 = c2.index(p2)
                d1 = statements()
                for pred in c1:
                    d1.add(pred[:])
                d2 = statements()
                for pred in c2:
                    d2.add(pred[:])
                standardA(d1, d2)
                sub = unify(d1.predicates[i1], d2.predicates[i2], {})
                if sub != None:
                    a1 = d1.predicates
                    a1.pop(i1)
                    a2 = d2.predicates
                    a2.pop(i2)
                    tmp = a1 + a2
                    if tmp == []:
                        return [None]
                    else:
                        n = statements(tmp)
                        n.AS(sub)
                        n.norm()
                        n.sort()
                        ans.append(n)
    return ans

def resolution(kB, query, depth):
    global startTime
    if depth == 5000 or time.time() - startTime > 5:
        return
    p = []
    for i in kB.clauses:
        if resolve(i, query):
            p.append((i, query))
        else:
            continue
    i = 1
    while i <= 1:
        l = len(p)
        for i in range(l):
            resolvents = resolveTwo(p[i])
            if resolvents == [None]:
                return True
            for c in resolvents:
                k = c.ToStr()
                if k not in kB.kBS:
                    kB.kBS.add(k)
                    if resolution(kB, c, depth + 1):
                        return True
        p = []
        i += 1
    return False


def sortKB(kB):
    pairs = []
    for cl in kB.clauses:
        s = set()
        for p in cl.predicates:
            for i in range(2, len(p)):
                if isVariable(p[i]) and p[i] not in s:
                    s.add(p[i])
        c = len(s)
        pairs.append((cl, c))
    pairs.sort(key=lambda x: x[1])
    leng = len(kB.clauses)
    for i in range(leng):
        kB.clauses[i] = pairs[i][0]


def main():
    global queryNumber, KbNumber, que, strkb, startTime
    que = []
    strkb = []
    startTime = 0
    O = KB()
    sys.setrecursionlimit(10000)
    input = open("input.txt", "r")
    s = input.readline()
    s = int(s)
    queryNumber = s
    for i in range(queryNumber):
        a = input.readline().rstrip()
        que.append(a)
    a = input.readline()
    a = int(a)
    KbNumber = a
    for i in range(KbNumber):
        tmp = input.readline().rstrip()
        tmp = CNF(tmp)
        strkb.append(tmp)
        O.input(strkb[i])
    input.close()


    output = open("output.txt", "w")
    OO = copy.deepcopy(O)
    sortKB(OO)
    length = len(OO.clauses)
    for i in range(queryNumber):
        del OO.clauses[length:]
        OO.kBS = copy.deepcopy(O.kBS)
        # tmp = que[i][1:] if que[i][0] == '~' else '~' + que[i]
        quer = parse(que[i][1:] if que[i][0] == '~' else '~' + que[i])
        OO.input(que[i][1:] if que[i][0] == '~' else '~' + que[i])
        startTime = time.time()
        depth = 1
        result = resolution(OO, quer, depth)
        if result:
            if i != queryNumber - 1:
                output.write("TRUE\n")
            else:
                output.write('TRUE')
        else:
            if i != queryNumber - 1:
                output.write("FALSE\n")
            else:
                output.write('FALSE')


if __name__ == "__main__":
    main()