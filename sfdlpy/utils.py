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
        click.echo(style(v, fg='green', bg='black'))


def style(v, **kwargs):
    if kwargs.get('fg') is None:
        kwargs['fg'] = 'green'
    if kwargs.get('bg') is None:
        kwargs['bg'] = 'black'
    return click.style(v, **kwargs)


def get_dl_speed(time, size):  # size in bytes plz
    speed = round(size / time)
    return '%.2f%s/s' % _transform_size(speed)


def get_speedreport(time, size):  # size in bytes plz
    speed = get_dl_speed(time, size)
    size, unit = _transform_size(size)
    return 'Loaded %.2f %s in %.2fs. Speed: %s' % (size, unit, time, speed)


def __flush(formatter=formatter):
    formatter.buffer = []


def _transform_size(size):
    unit = 'B'
    if size >= 1024:
        unit = 'KB'
        size = size / 1024
        if size >= 1024:
            unit = 'MB'
            size = size / 1024
            if size >= 1024:
                unit = 'GB'
                size = size / 1024
    return (size, unit)
