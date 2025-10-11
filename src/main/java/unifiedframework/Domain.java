package unifiedframework;

import java.math.BigDecimal;

@SuppressWarnings({"deprecation", "BigDecimalLegacyMethod"})
public class Domain {

    private final BigDecimal z;
    private final BigDecimal a;
    private final BigDecimal b;
    private final BigDecimal c;
    private static final int PRECISION = 100;
    private static final int ROUNDING_MODE = BigDecimal.ROUND_HALF_UP;

    public Domain(
            int n
    ) {
        // z = a (b/c)
        a = new BigDecimal(n);
        b = new BigDecimal(n);
        c = new BigDecimal("2.718281828459045");
        BigDecimal x = b.divide(c, PRECISION, ROUNDING_MODE);
        z = a.multiply(x);

    }

    public double getZ() {
        return z.doubleValue();
    }

    public double getA() {
        return a.doubleValue();
    }

    public double getB() {
        return b.doubleValue();
    }

    public double getC() {
        return c.doubleValue();
    }

    // begin Fibonacci sequence for getters...

    public double getD(){
        return b.divide(c, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getE(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        return c.divide(d, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getF(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        return d.divide(e, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getG(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        return e.divide(f, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getH(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        return f.divide(g, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getI(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        return g.divide(h, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getJ(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        return h.divide(i, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getK(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        return i.divide(j, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getL(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        return j.divide(k, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getM(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        return k.divide(l, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getN(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        return l.divide(m, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getO(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        return m.divide(n, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getP(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        return n.divide(o, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getQ(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        return o.divide(p, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getR(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        return p.divide(q, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getS(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        return q.divide(r, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getT(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        BigDecimal s = q.divide(r, PRECISION, ROUNDING_MODE);
        return r.divide(s, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getU(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        BigDecimal s = q.divide(r, PRECISION, ROUNDING_MODE);
        BigDecimal t = r.divide(s, PRECISION, ROUNDING_MODE);
        return s.divide(t, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getV(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        BigDecimal s = q.divide(r, PRECISION, ROUNDING_MODE);
        BigDecimal t = r.divide(s, PRECISION, ROUNDING_MODE);
        BigDecimal u = s.divide(t, PRECISION, ROUNDING_MODE);
        return t.divide(u, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getW(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        BigDecimal s = q.divide(r, PRECISION, ROUNDING_MODE);
        BigDecimal t = r.divide(s, PRECISION, ROUNDING_MODE);
        BigDecimal u = s.divide(t, PRECISION, ROUNDING_MODE);
        BigDecimal v = t.divide(u, PRECISION, ROUNDING_MODE);
        return u.divide(v, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getX(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        BigDecimal s = q.divide(r, PRECISION, ROUNDING_MODE);
        BigDecimal t = r.divide(s, PRECISION, ROUNDING_MODE);
        BigDecimal u = s.divide(t, PRECISION, ROUNDING_MODE);
        BigDecimal v = t.divide(u, PRECISION, ROUNDING_MODE);
        BigDecimal w = u.divide(v, PRECISION, ROUNDING_MODE);
        return v.divide(w, PRECISION, ROUNDING_MODE).doubleValue();
    }

    public double getY(){
        BigDecimal d = b.divide(c, PRECISION, ROUNDING_MODE);
        BigDecimal e = c.divide(d, PRECISION, ROUNDING_MODE);
        BigDecimal f = d.divide(e, PRECISION, ROUNDING_MODE);
        BigDecimal g = e.divide(f, PRECISION, ROUNDING_MODE);
        BigDecimal h = f.divide(g, PRECISION, ROUNDING_MODE);
        BigDecimal i = g.divide(h, PRECISION, ROUNDING_MODE);
        BigDecimal j = h.divide(i, PRECISION, ROUNDING_MODE);
        BigDecimal k = i.divide(j, PRECISION, ROUNDING_MODE);
        BigDecimal l = j.divide(k, PRECISION, ROUNDING_MODE);
        BigDecimal m = k.divide(l, PRECISION, ROUNDING_MODE);
        BigDecimal n = l.divide(m, PRECISION, ROUNDING_MODE);
        BigDecimal o = m.divide(n, PRECISION, ROUNDING_MODE);
        BigDecimal p = n.divide(o, PRECISION, ROUNDING_MODE);
        BigDecimal q = o.divide(p, PRECISION, ROUNDING_MODE);
        BigDecimal r = p.divide(q, PRECISION, ROUNDING_MODE);
        BigDecimal s = q.divide(r, PRECISION, ROUNDING_MODE);
        BigDecimal t = r.divide(s, PRECISION, ROUNDING_MODE);
        BigDecimal u = s.divide(t, PRECISION, ROUNDING_MODE);
        BigDecimal v = t.divide(u, PRECISION, ROUNDING_MODE);
        BigDecimal w = u.divide(v, PRECISION, ROUNDING_MODE);
        BigDecimal x = v.divide(w, PRECISION, ROUNDING_MODE);
        return w.divide(x, PRECISION, ROUNDING_MODE).doubleValue();
    }
}
