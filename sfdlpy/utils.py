import click

formatter = click.HelpFormatter(indent_increment=4, max_width=120)


def print_section(name, values, formatter=formatter):
    with formatter.section(name=click.style(name, bold=True, underline=True)):
        formatter.write_dl(values)
        click.echo(formatter.getvalue())
        __flush()


def echo(v, debug=False):
    if debug:
        print(v)
    else:
        click.echo(click.style(
            v, fg='green', bg='black'
        ))


def __flush(formatter=formatter):
    formatter.buffer = []


def get_dl_speed(time, size):  # size in bytes plz
    unit = 'B'
    if size >= 1024:
        unit = 'kB'
        size = size / 1024
        if size >= 1024:
            unit = 'mB'
            size = size / 1024
    speed = round(size / time)
    return '%i%s/s' % (speed, unit)


def get_speedreport(time, size):  # size in bytes plz
    speed = get_dl_speed(time, size)
    return 'Loaded %ibytes in %is. Speed: %s' % (size, time, speed)
