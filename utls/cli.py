# -*- coding: utf-8 -*-

import click
from latex import command_to_latex

@click.group(chain=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    """Console script for utls"""
    ctx.obj['DEBUG'] = debug


@cli.command()
@click.argument("equation")
@click.pass_context
def com(ctx, equation):
    ctx.obj['LATEX'] = command_to_latex(equation)
    click.echo(ctx.obj['LATEX'])

@cli.command()
@click.pass_context
def show(ctx):
    """
    you need to install texlive-latex-extra and texlive-fonts-recommended.
    http://stackoverflow.com/questions/11354149/python-unable-to-render-tex-in-matplotlib/11357765#11357765
    """
    import numpy as np
    import matplotlib.pyplot as plt

    # Example data
    t = np.arange(0.0, 1.0 + 0.01, 0.01)
    s = np.cos(4 * np.pi * t) + 2

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.plot(t, s)

    plt.xlabel(r'\textbf{time} (s)')
    plt.ylabel(r'\textit{voltage} (mV)', fontsize=16)
    plt.title(r"\TeX\ is Number "
              r"$\displaystyle\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$!",
              fontsize=16, color='gray')
    # Make room for the ridiculously large title.
    plt.subplots_adjust(top=0.8)

    plt.savefig('tex_demo')
    plt.show()


if __name__ == "__main__":
    cli(obj={})
