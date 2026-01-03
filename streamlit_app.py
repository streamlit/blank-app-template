import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
    import streamlit as st
import sympy as sp
import pandas as pd

# Judul Aplikasi
st.title("Aplikasi Web Solusi SPNL")
st.subheader("Metode Bisection")

st.write("""
Metode Bisection digunakan untuk mencari akar dari persamaan nonlinear 
dengan membagi interval secara berulang hingga diperoleh solusi mendekati nol.
""")

# Input persamaan
x = sp.symbols('x')
fungsi_input = st.text_input("Masukkan fungsi f(x):", "x**3 - x - 2")

# Input parameter
a = st.number_input("Batas bawah (a):", value=1.0)
b = st.number_input("Batas atas (b):", value=2.0)
toleransi = st.number_input("Toleransi error:", value=0.0001)
max_iter = st.number_input("Maksimum iterasi:", value=20, step=1)

if st.button("Hitung Akar"):
    try:
        f = sp.sympify(fungsi_input)
        f_lambdified = sp.lambdify(x, f)

        fa = f_lambdified(a)
        fb = f_lambdified(b)

        if fa * fb > 0:
            st.error("f(a) dan f(b) harus memiliki tanda yang berbeda!")
        else:
            data = []
            iterasi = 1

            while iterasi <= max_iter:
                c = (a + b) / 2
                fc = f_lambdified(c)

                data.append([iterasi, a, b, c, fc])

                if abs(fc) < toleransi:
                    break

                if fa * fc < 0:
                    b = c
                    fb = fc
                else:
                    a = c
                    fa = fc

                iterasi += 1

            df = pd.DataFrame(
                data,
                columns=["Iterasi", "a", "b", "c (Akar)", "f(c)"]
            )

            st.success("Perhitungan selesai!")
            st.write("### Tabel Iterasi Metode Bisection")
            st.dataframe(df)

            st.write(f"### Akar Hampiran = {c}")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

)
