import os
import sys
import click

from apposlc import create_oslc_app


def get_env():
    """Get the environment the app is running in, indicated by the
    :envvar:`PYOSLC_ENV` environment variable. The default is
    ``'production'``.
    """
    return os.environ.get('PYOSLC_ENV') or 'production'


def show_server_banner(env, debug, app_import_path, eager_loading):
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        return

    if app_import_path is not None:
        message = ' * Serving PyOSLC app "{0}"'.format(app_import_path)

        if not eager_loading:
            message += ' (lazy loading)'

        click.echo(message)

    click.echo(' * Environment: {0}'.format(env))

    if env == 'production':
        click.secho(
            '   WARNING: Do not use the development server in a production'
            ' environment.', fg='red')
        click.secho('   Use a production WSGI server instead.', dim=True)

    if debug is not None:
        click.echo(' * Debug mode: {0}'.format('on' if debug else 'off'))


@click.command('run', short_help='Runs a development server.')
@click.option('--host', '-h', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('--reload/--no-reload', default=None,
              help='Enable or disable the reloader. By default the reloader '
              'is active if debug is enabled.')
@click.option('--debugger/--no-debugger', default=None,
              help='Enable or disable the debugger. By default the debugger '
              'is active if debug is enabled.')
@click.option('--eager-loading/--lazy-loader', default=None,
              help='Enable or disable eager loading. By default eager '
              'loading is enabled if the reloader is disabled.')
@click.option('--with-threads/--without-threads', default=True,
              help='Enable or disable multithreading.')
def run_command(host, port, reload, debugger, eager_loading,
                with_threads):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    PYOSLC_ENV=development or PYOSLC_DEBUG=1.
    """
    debug = True

    # if reload is None:
    #    reload = debug

    if debugger is None:
        debugger = debug

    if eager_loading is None:
        eager_loading = not reload

    show_server_banner(get_env(), debug, '/oslc', eager_loading)
    # app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    from werkzeug.serving import run_simple
    app = create_oslc_app()
    run_simple(host, port, app, use_reloader=reload, use_debugger=debugger, threaded=with_threads)


cli = click.Group(help='run')
cli.add_command(run_command)


def main(as_module=False):
    args = sys.argv[1:]

    if as_module:
        this_module = 'pyoslc'

        if sys.version_info < (2, 7):
            this_module += '.cli'

        name = 'python -m ' + this_module

        # Python rewrites "python -m pyoslc" to the path to the file in argv.
        # Restore the original command so that the reloader works.
        sys.argv = ['-m', this_module] + args
    else:
        name = None

    cli.main(args=args, prog_name=name)


if __name__ == '__main__':
    main(as_module=True)
