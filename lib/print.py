import click

formatter = click.HelpFormatter(indent_increment=4, max_width=120)

def print_section(name, values, formatter=formatter):
    with formatter.section(name=click.style(name, bold=True, underline=True)):
        formatter.write_dl(values)
        click.echo(formatter.getvalue())
        __flush()


def echo(v, debug=False):
    if debug: print(v)
    else: click.echo(v)

def __flush(formatter=formatter):
    formatter.buffer = []
