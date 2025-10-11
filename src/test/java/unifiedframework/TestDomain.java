package unifiedframework;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TestDomain {
    @Test
    public void testGetters() {
        Domain d = new Domain(1);
        double delta = 1e-10;

        // Test existing getters
        assertEquals(d.getB() / d.getC(), d.getD(), delta);
        assertEquals(d.getC() / d.getD(), d.getE(), delta);
        assertEquals(d.getD() / d.getE(), d.getF(), delta);

        // Test new getters
        assertEquals(d.getE() / d.getF(), d.getG(), delta);
        assertEquals(d.getF() / d.getG(), d.getH(), delta);
        assertEquals(d.getG() / d.getH(), d.getI(), delta);
        assertEquals(d.getH() / d.getI(), d.getJ(), delta);
        assertEquals(d.getI() / d.getJ(), d.getK(), delta);
        assertEquals(d.getJ() / d.getK(), d.getL(), delta);
        assertEquals(d.getK() / d.getL(), d.getM(), delta);
        assertEquals(d.getL() / d.getM(), d.getN(), delta);
        assertEquals(d.getM() / d.getN(), d.getO(), delta);
        assertEquals(d.getN() / d.getO(), d.getP(), delta);
        assertEquals(d.getO() / d.getP(), d.getQ(), delta);
        assertEquals(d.getP() / d.getQ(), d.getR(), delta);
        assertEquals(d.getQ() / d.getR(), d.getS(), delta);
        assertEquals(d.getR() / d.getS(), d.getT(), delta);
        assertEquals(d.getS() / d.getT(), d.getU(), delta);
        assertEquals(d.getT() / d.getU(), d.getV(), delta);
        assertEquals(d.getU() / d.getV(), d.getW(), delta);
        assertEquals(d.getV() / d.getW(), d.getX(), delta);
        assertEquals(d.getW() / d.getX(), d.getY(), delta);
    }
}
