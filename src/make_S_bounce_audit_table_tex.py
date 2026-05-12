"""S_bounce reproducibility audit table.

Emits a per-step audit table for the bounce-action derivation
of Section~\\ref{sec:bounce-action}. The table makes every
ingredient that goes into the numerical value
$S_{\\rm bounce}=37.995389$ explicit (field content, background,
action, boundary conditions, EOM, saddle search, negative
mode, uncertainty), with the canonical input source and the
verifying numerical certificate for each row. The numerical
values are read from \\texttt{data/ew\\_scale\\_inputs.json}
so that any update of the canonical inputs propagates here on
the next generator run.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "data" / "ew_scale_inputs.json"
OUT = REPO / "paper" / "tables" / "tab_S_bounce_audit.tex"
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    eta_S = data["inputs"]["eta_S_P1"]
    s_b = data["inputs"]["S_bounce_P1"]

    rows = [
        ("(i)", "Field content",
         r"two real scalars $\varphi$ (carrier) and $\Xi$ "
         r"(unique negative mode)",
         r"Sec.~\ref{sec:bounce-action} step (i)",
         "---"),
        ("(ii)", "Background geometry",
         r"Euclidean four-sphere $S^{4}$, FL coordinates "
         r"\eqref{eq:S4metric}",
         r"Sec.~\ref{sec:bounce-action} step (ii); "
         r"\cite{CamporesiHiguchi1996}",
         r"$\xi=1/6$"),
        ("(iii)", "Euclidean action",
         r"Coleman--Callan-Coleman action \eqref{eq:SE} with "
         r"potential \eqref{eq:Vphi}",
         r"\cite{Coleman1977,CallanColeman1977}",
         "---"),
        ("(iv)", "Boundary conditions",
         r"$\varphi_{B}'(0)=0$; $\varphi_{B}(\sigma\to\pi)\to "
         r"\varphi_{\rm false}$",
         r"Sec.~\ref{sec:bounce-action} step (iv) "
         r"\eqref{eq:BCs}",
         "---"),
        ("(v)", "Equation of motion",
         r"$\frac{1}{\rho_{0}^{2}\sin^{3}\sigma}\partial_{\sigma}"
         r"(\sin^{3}\sigma\,\partial_{\sigma}\varphi_{B})="
         r"V'(\varphi_{B})$",
         r"Sec.~\ref{sec:bounce-action} step (v) "
         r"\eqref{eq:EOM}",
         "---"),
        ("(vi)", "Saddle search (Sommerfeld)",
         r"$\eta_{S}\!=\!\frac{1}{2\pi}\!\int_{\sigma_{-}}^{\sigma_{+}}\!"
         r"\sqrt{2V_{\rm eff}/\rho_{0}^{2}}\,\mathrm{d}\sigma$",
         r"\texttt{src/recompute\_ew\_scale.py}; "
         r"\texttt{data/ew\_scale\_inputs.json}",
         f"$\\eta_{{S}}={eta_S:.6f}$"),
        ("(vii)", "Bounce action",
         r"$S_{\rm bounce}\!=\!4\pi\eta_{S}$ "
         r"(Coleman normalisation)",
         r"\eqref{eq:etaS-num}",
         f"$S_{{\\rm bounce}}={s_b:.6f}$"),
        ("(viii)", "Unique negative mode",
         r"single normalisable mode $u_{0}$ on the bounce "
         r"trajectory; second-variation operator has unique "
         r"negative eigenvalue",
         r"Sec.~\ref{sec:wick}; "
         r"\cite{Coleman1977}",
         "---"),
        ("(ix)", "Saddle-vs-back-fit guard",
         r"$\eta_{S}$ integration uses only $V$, $\rho_{0}$, "
         r"$V_{0}$, $m_{\varphi}^{\rm op,2}\rho_{0}^{2}=-4$; "
         r"no $v_{\rm EW}$ input",
         r"Sec.~\ref{sec:bounce-action} step (vii); "
         r"falsification axiom F1",
         r"window $[3.019,3.027]$"),
        ("(x)", "Numerical uncertainty",
         r"residual of saddle integration at bundled grid "
         r"resolution",
         r"\eqref{eq:etaS-num}",
         r"$\Delta\eta_{S}\!\approx\!5\!\times\!10^{-6}$"),
        ("(xi)", "T-parity source axiom",
         r"$\eta_{T}(\Xi)=-1$ from $S_{b}>0$ + CPT + "
         r"hermiticity (Theorem on bounce sector)",
         r"Theorem~\ref{thm:t-parity-uniqueness}",
         "---"),
    ]

    lines = []
    A = lines.append
    A(r"\begin{tabular}{@{}l p{0.16\textwidth} "
      r"p{0.36\textwidth} p{0.20\textwidth} p{0.16\textwidth}@{}}")
    A(r"\toprule")
    A(r"Step & Item & Specification & Source / verified by & "
      r"Value \\")
    A(r"\midrule")
    for step, item, spec, source, value in rows:
        A(f"{step} & {item} & {spec} & {source} & {value} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}  ({len(rows)} steps)")


if __name__ == "__main__":
    main()
