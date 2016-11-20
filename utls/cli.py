# -*- coding: utf-8 -*-

import click
from latex import command_to_latex
from functools import update_wrapper


@click.group(chain=True)
def cli():
    """This script converts Python-formatted equations in Latex. One commands feeds into the next.

    Example:

    \b
        utls open -e example01.jpg resize -w 128 display
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
        def processor(stream):
            return f(stream, *args, **kwargs)
        return processor
    return update_wrapper(new_func, f)


def generator(f):
    """Similar to the :func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    """
    @processor
    def new_func(stream, *args, **kwargs):
        for item in stream:
            yield item
        for item in f(*args, **kwargs):
            yield item
    return update_wrapper(new_func, f)


@cli.command('equation')
@click.option('-e', '--equations', type=click.STRING,
              multiple=True, help='Python equations.')
@generator
def equation(equations):
    for eq in equations:
        click.echo("Input: {}".format(eq))
        yield eq

@cli.command('py2latex')
@processor
def py2latex(equations):
    """
    Convert from Python to Latex."""
    for eq in equations:
        converted = command_to_latex(eq)
        click.echo("{} -> {}".format(eq, converted))
        yield converted

@cli.command('fig')
@click.option('--separate', is_flag=True)
@click.option('--show', is_flag=True)
@click.option('--save', is_flag=True)
@click.option('--filename', default='processed-{}.png', type=click.Path(),
              help='The format for the filename.',
              show_default=True)
@processor
def fig(latex_eqs, separate=False, filename='processed-{}.png', show=False, save=False):
    """
    Place latex equations in a Matplotlib figure.

    Make sure you have installed texlive-latex-extra and texlive-fonts-recommended:
    http://stackoverflow.com/questions/11354149/python-unable-to-render-tex-in-matplotlib/11357765#11357765
    """
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams['text.latex.unicode'] = True

    if not separate:
        alleqs = "\n".join(latex_eqs)
        fig = plt.figure(figsize=(3, 1))
        fig.text(0.1, 0.5, alleqs, size=24, va='center')

        if show:
            plt.show()
        if save:
            plt.savefig(filename.format("all"))
    else:
        for i, eq in enumerate(latex_eqs):
            fig = plt.figure(figsize=(3, 1))
            fig.text(0.1, 0.5, eq, size=24, va='center')

            if show:
                plt.show()
            if save:
                plt.savefig(filename.format(i))
            yield eq

def main():
    cli(obj={})

if __name__ == "__main__":
    import sys
    print sys.argv
    main()
