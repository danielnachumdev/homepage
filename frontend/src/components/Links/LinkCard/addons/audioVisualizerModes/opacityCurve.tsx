type Token =
    | { type: 'number'; value: number }
    | { type: 'var'; name: 'x' }
    | { type: 'op'; op: '+' | '-' | '*' | '/' | '^' }
    | { type: 'lparen' }
    | { type: 'rparen' };

const precedence: Record<Token & { type: 'op' }['op'], number> = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
};

const rightAssociative = new Set<Token & { type: 'op' }['op']>(['^']);

function tokenize(expr: string): Token[] {
    const s = expr.replace(/\s+/g, '');
    const tokens: Token[] = [];

    let i = 0;
    while (i < s.length) {
        const ch = s[i];

        if (ch === '(') {
            tokens.push({ type: 'lparen' });
            i++;
            continue;
        }
        if (ch === ')') {
            tokens.push({ type: 'rparen' });
            i++;
            continue;
        }
        if (ch === 'x' || ch === 'X') {
            tokens.push({ type: 'var', name: 'x' });
            i++;
            continue;
        }
        if (ch === '+' || ch === '-' || ch === '*' || ch === '/' || ch === '^') {
            // unary minus: treat as 0 - ...
            const prev = tokens[tokens.length - 1];
            const isUnaryMinus = ch === '-' && (!prev || prev.type === 'op' || prev.type === 'lparen');
            if (isUnaryMinus) {
                tokens.push({ type: 'number', value: 0 });
                tokens.push({ type: 'op', op: '-' });
                i++;
                continue;
            }
            tokens.push({ type: 'op', op: ch as any });
            i++;
            continue;
        }

        // number
        if (ch >= '0' && ch <= '9' || ch === '.') {
            let j = i + 1;
            while (j < s.length) {
                const c = s[j];
                if ((c >= '0' && c <= '9') || c === '.') j++;
                else break;
            }
            const raw = s.slice(i, j);
            const value = Number(raw);
            if (!Number.isFinite(value)) throw new Error(`Invalid number: "${raw}"`);
            tokens.push({ type: 'number', value });
            i = j;
            continue;
        }

        throw new Error(`Unsupported character "${ch}" in opacity curve`);
    }

    return tokens;
}

function toRpn(tokens: Token[]): Token[] {
    const out: Token[] = [];
    const stack: Token[] = [];

    for (const t of tokens) {
        if (t.type === 'number' || t.type === 'var') {
            out.push(t);
            continue;
        }

        if (t.type === 'op') {
            while (stack.length) {
                const top = stack[stack.length - 1];
                if (top.type !== 'op') break;
                const pTop = precedence[top.op];
                const pCur = precedence[t.op];
                const shouldPop = rightAssociative.has(t.op) ? pTop > pCur : pTop >= pCur;
                if (!shouldPop) break;
                out.push(stack.pop()!);
            }
            stack.push(t);
            continue;
        }

        if (t.type === 'lparen') {
            stack.push(t);
            continue;
        }

        if (t.type === 'rparen') {
            while (stack.length && stack[stack.length - 1].type !== 'lparen') {
                out.push(stack.pop()!);
            }
            if (!stack.length || stack[stack.length - 1].type !== 'lparen') {
                throw new Error('Mismatched parentheses in opacity curve');
            }
            stack.pop(); // pop lparen
            continue;
        }
    }

    while (stack.length) {
        const t = stack.pop()!;
        if (t.type === 'lparen' || t.type === 'rparen') throw new Error('Mismatched parentheses in opacity curve');
        out.push(t);
    }

    return out;
}

function clamp01(v: number): number {
    if (!Number.isFinite(v)) return 0;
    if (v <= 0) return 0;
    if (v >= 1) return 1;
    return v;
}

export function compileOpacityCurve(expr: string): (x: number) => number {
    const tokens = toRpn(tokenize(expr));

    return (x: number) => {
        const stack: number[] = [];

        for (const t of tokens) {
            if (t.type === 'number') {
                stack.push(t.value);
                continue;
            }
            if (t.type === 'var') {
                stack.push(x);
                continue;
            }
            if (t.type === 'op') {
                const b = stack.pop();
                const a = stack.pop();
                if (a === undefined || b === undefined) return 0;
                switch (t.op) {
                    case '+':
                        stack.push(a + b);
                        break;
                    case '-':
                        stack.push(a - b);
                        break;
                    case '*':
                        stack.push(a * b);
                        break;
                    case '/':
                        stack.push(b === 0 ? 0 : a / b);
                        break;
                    case '^':
                        stack.push(Math.pow(a, b));
                        break;
                    default: {
                        const _exhaustive: never = t.op;
                        return _exhaustive;
                    }
                }
                continue;
            }
        }

        if (stack.length !== 1) return 0;
        return clamp01(stack[0]);
    };
}

