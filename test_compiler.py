from compiler import main


class TestCompiler:
    def test_var_assign(self):
        program = "{ var_12=11; }"
        res = main(program)
        assert res == "var_12=11\n"

    def test_two_var_assign(self):
        program = "{ j=11; i=8; }"
        res = main(program)
        assert res == "j=11\ni=8\n"

    def test_unary_minus(self):
        res = main("{ i=-55; }")
        assert res == "i=-55\n"

    def test_unary_plus(self):
        res = main("{ amount=+55; }")
        assert res == "amount=55\n"

    def test_multiple_assign(self):
        program = "a=b=c=2<3;"
        res = main(program)
        assert res == "c=1\nb=1\na=1\n"

    def test_sum(self):
        program = "{ i=2+5; }"
        res = main(program)
        assert res == "i=7\n"

    def test_sub(self):
        program = "{ i=2-5; }"
        res = main(program)
        assert res == "i=-3\n"
    
    def test_mult(self):
        program = "{ i=6*8/3; }"
        res = main(program)
        assert res == "i=16\n"
    
    def test_if_true(self):
        program = "{ i=7; if (i<6) x=1; }"
        res = main(program)
        assert res == "i=7\n"

    def test_if_false(self):
        program = "{ i=7; if (i<6) x=1; }"
        res = main(program)
        assert res == "i=7\n"

    def test_if_else(self):
        program = "{ i=7; if (i<8) x=2; else x=6; }"
        res = main(program)
        assert res == "i=7\nx=2\n"

    def test_while_loop(self):
        program = "{ i=1; while ((i=i+10)<50); }"
        res = main(program)
        assert res == "i=51\n"

    def test_while_loop_with_expr(self):
        program = "{ i=1; while ((i=i+10)<50) { i=i+1; } }"
        res = main(program)
        assert res == "i=55\n"

    def test_while_and_if_else(self):
        program = \
        """{i=125; 
            j=100; 
            while (i-j) 
            if (i<j) 
                j=j-i; 
            else 
                i=i-j; }"""
        res = main(program)
        assert res == "i=25\nj=25\n"

    def test_for_loop(self):
        program = "{ x=0; for (i=0; i<5; i=i+1) x=x+2; }"
        res = main(program)
        assert res == "x=10\ni=5\n"

    def test_gt_compar(self):
        program = "{ i=10; while (i>5) i=i-1; }"
        res = main(program)
        assert res == "i=5\n"

    def test_ge_compar(self):
        program = "{ i=10; do i=i-1; while (i>=5); }"
        res = main(program)
        assert res == "i=4\n"

    def test_lt_compar(self):
        program = "{ i=0; while (i<5) i=i+1; }"
        res = main(program)
        assert res == "i=5\n"

    def test_le_compar(self):
        program = "{ i=0; do i=i+1; while (i<=5); }"
        res = main(program)
        assert res == "i=6\n"

    def test_eq_compar(self):
        program = "{ i=5; if (i==5) x=2; }"
        res = main(program)
        assert res == "i=5\nx=2\n"

    def test_ne_compar(self):
        program = "{ i=10; while (i#5) i=i-1; }"
        res = main(program)
        assert res == "i=5\n"