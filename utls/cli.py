# -*- coding: utf-8 -*-

import click
from latex import command_to_latex
from functools import wraps, update_wrapper


@click.group(chain=True)
def cli():
    """This script processes a bunch of images through pillow in a unix
    pipe.  One commands feeds into the next.
    Example:
    \b
        imagepipe open -i example01.jpg resize -w 128 display
        imagepipe open -i example02.jpg blur save
    """

@cli.resultcallback()
def process_commands(processors):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    # Start with an empty iterable.
    stream = ()

    # Pipe it through all stream processors.
    for processor in processors:
        stream = processor(stream)

    # Evaluate the stream and throw away the items.
    for _ in stream:
        pass


def processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """
    def new_func(*args, **kwargs):
        #@wraps
        def processor(stream):
            return f(stream, *args, **kwargs)
        return processor
    #return new_func
    return update_wrapper(new_func, f)


def generator(f):
    """Similar to the :func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    """
    #@wraps
    @processor
    def new_func(stream, *args, **kwargs):
        for item in stream:
            yield item
        for item in f(*args, **kwargs):
            yield item
    #return new_func
    return update_wrapper(new_func, f)



@cli.command('com')
@click.option('-e', '--equations',
              multiple=True, help='Python equations.')
@generator
def com(equations):
    for eq in equations:
        click.echo(eq)
        yield command_to_latex(eq)


@cli.command('show')
@processor
def show(latex_eqs):
    """
    you need to install texlive-latex-extra and texlive-fonts-recommended.
    http://stackoverflow.com/questions/11354149/python-unable-to-render-tex-in-matplotlib/11357765#11357765
    """
    import numpy as np
    import matplotlib.pyplot as plt

    for eq in latex_eqs:
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
