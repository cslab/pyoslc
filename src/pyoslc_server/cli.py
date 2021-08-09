import ast
import inspect
import os
import platform
import re
import sys
import traceback
import warnings
from functools import update_wrapper
from threading import Lock, Thread

import click
from werkzeug.utils import import_string

try:
    import dotenv
except ImportError:
    dotenv = None


class NoAppException(click.UsageError):
    """Raised if an application cannot be found or loaded."""


def find_best_app(script_info, module):
    """Given a module instance this tries to find the best possible
    application in the module or raises an exception.
    """
    from pyoslc_server.api import OSLCAPI

    # Search for the most common names first.
    for attr_name in ("app", "application"):
        app = getattr(module, attr_name, None)

        if isinstance(app, OSLCAPI):
            return app

    # Otherwise find the only object that is a OSLCAPI instance.
    matches = [v for v in module.__dict__.values() if isinstance(v, OSLCAPI)]

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            "Detected multiple PyOSLC applications in module"
            f" {module.__name__!r}. Use 'PYOSLC_APP={module.__name__}:name'"
            f" to specify the correct one."
        )

    # Search for app factory functions.
    for attr_name in ("create_app", "make_app"):
        app_factory = getattr(module, attr_name, None)

        if inspect.isfunction(app_factory):
            try:
                app = call_factory(script_info, app_factory)

                if isinstance(app, OSLCAPI):
                    return app
            except TypeError:
                if not _called_with_wrong_args(app_factory):
                    raise
                raise NoAppException(
                    f"Detected factory {attr_name!r} in module {module.__name__!r},"
                    " but could not call it without arguments. Use"
                    f" \"PYOSLC_APP='{module.__name__}:{attr_name}(args)'\""
                    " to specify arguments."
                )

    raise NoAppException(
        "Failed to find PyOSLC application or factory in module"
        f" {module.__name__!r}. Use 'PYOSLC_APP={module.__name__}:name'"
        " to specify one."
    )


def call_factory(script_info, app_factory, args=None, kwargs=None):
    """Takes an app factory, a ``script_info` object and  optionally a tuple
    of arguments. Checks for the existence of a script_info argument and calls
    the app_factory depending on that and the arguments provided.
    """
    sig = inspect.signature(app_factory)
    args = [] if args is None else args
    kwargs = {} if kwargs is None else kwargs

    if "script_info" in sig.parameters:
        warnings.warn(
            "The 'script_info' argument is deprecated and will not be"
            " passed to the app factory function in PyOSLC 2.1.",
            DeprecationWarning,
        )
        kwargs["script_info"] = script_info

    if (
        not args
        and len(sig.parameters) == 1
        and next(iter(sig.parameters.values())).default is inspect.Parameter.empty
    ):
        warnings.warn(
            "Script info is deprecated and will not be passed as the"
            " single argument to the app factory function in PyOSLC"
            " 2.1.",
            DeprecationWarning,
        )
        args.append(script_info)

    return app_factory(*args, **kwargs)


def _called_with_wrong_args(f):
    """Check whether calling a function raised a ``TypeError`` because
    the call failed or because something in the factory raised the
    error.

    :param f: The function that was called.
    :return: ``True`` if the call failed.
    """
    tb = sys.exc_info()[2]

    try:
        while tb is not None:
            if tb.tb_frame.f_code is f.__code__:
                # In the function, it was called successfully.
                return False

            tb = tb.tb_next

        # Didn't reach the function.
        return True
    finally:
        # Delete tb to break a circular reference.
        # https://docs.python.org/2/library/sys.html#sys.exc_info
        del tb


def find_app_by_string(script_info, module, app_name):
    """Check if the given string is a variable name or a function. Call
    a function to get the app instance, or return the variable directly.
    """
    from pyoslc_server.api import OSLCAPI

    # Parse app_name as a single expression to determine if it's a valid
    # attribute name or function call.
    try:
        expr = ast.parse(app_name.strip(), mode="eval").body
    except SyntaxError:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )

    if isinstance(expr, ast.Name):
        name = expr.id
        args = kwargs = None
    elif isinstance(expr, ast.Call):
        # Ensure the function name is an attribute name only.
        if not isinstance(expr.func, ast.Name):
            raise NoAppException(
                f"Function reference must be a simple name: {app_name!r}."
            )

        name = expr.func.id

        # Parse the positional and keyword arguments as literals.
        try:
            args = [ast.literal_eval(arg) for arg in expr.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in expr.keywords}
        except ValueError:
            # literal_eval gives cryptic error messages, show a generic
            # message with the full expression instead.
            raise NoAppException(
                f"Failed to parse arguments as literal values: {app_name!r}."
            )
    else:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )

    try:
        attr = getattr(module, name)
    except AttributeError:
        raise NoAppException(
            f"Failed to find attribute {name!r} in {module.__name__!r}."
        )

    # If the attribute is a function, call it with any args and kwargs
    # to get the real application.
    if inspect.isfunction(attr):
        try:
            app = call_factory(script_info, attr, args, kwargs)
        except TypeError:
            if not _called_with_wrong_args(attr):
                raise

            raise NoAppException(
                f"The factory {app_name!r} in module"
                f" {module.__name__!r} could not be called with the"
                " specified arguments."
            )
    else:
        app = attr

    if isinstance(app, OSLCAPI):
        return app

    raise NoAppException(
        "A valid PyOSLC application was not obtained from"
        f" '{module.__name__}:{app_name}'."
    )


def prepare_import(path):
    """Given a filename this will try to calculate the python path, add it
    to the search path and return the actual module name that is expected.
    """
    path = os.path.realpath(path)

    fname, ext = os.path.splitext(path)
    if ext == ".py":
        path = fname

    if os.path.basename(path) == "__init__":
        path = os.path.dirname(path)

    module_name = []

    # move up until outside package structure (no __init__.py)
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, "__init__.py")):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)

    return ".".join(module_name[::-1])


def locate_app(script_info, module_name, app_name, raise_if_not_found=True):
    __traceback_hide__ = True  # noqa: F841

    try:
        __import__(module_name)
    except ImportError:
        # Reraise the ImportError if it occurred within the imported module.
        # Determine this by checking whether the trace has a depth > 1.
        if sys.exc_info()[2].tb_next:
            raise NoAppException(
                f"While importing {module_name!r}, an ImportError was"
                f" raised:\n\n{traceback.format_exc()}"
            )
        elif raise_if_not_found:
            raise NoAppException(f"Could not import {module_name!r}.")
        else:
            return

    module = sys.modules[module_name]

    if app_name is None:
        return find_best_app(script_info, module)
    else:
        return find_app_by_string(script_info, module, app_name)


def get_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    import werkzeug
    from pyoslc import __version__

    click.echo(
        f"Python {platform.python_version()}\n"
        f"PyOSLC {__version__}\n"
        f"Werkzeug {werkzeug.__version__}",
        color=ctx.color,
    )
    ctx.exit()


version_option = click.Option(
    ["--version"],
    help="Show the PyOSLC version",
    expose_value=False,
    callback=get_version,
    is_flag=True,
    is_eager=True,
)


class DispatchingApp:
    """Special application that dispatches to a PyOSLC application which
    is imported by name in a background thread.  If an error happens
    it is recorded and shown as part of the WSGI handling which in case
    of the Werkzeug debugger means that it shows up in the browser.
    """

    def __init__(self, loader, use_eager_loading=None):
        self.loader = loader
        self._app = None
        self._lock = Lock()
        self._bg_loading_exc_info = None

        if use_eager_loading is None:
            use_eager_loading = os.environ.get("WERKZEUG_RUN_MAIN") != "true"

        if use_eager_loading:
            self._load_unlocked()
        else:
            self._load_in_background()

    def _load_in_background(self):
        def _load_app():
            __traceback_hide__ = True  # noqa: F841
            with self._lock:
                try:
                    self._load_unlocked()
                except Exception:
                    self._bg_loading_exc_info = sys.exc_info()

        t = Thread(target=_load_app, args=())
        t.start()

    def _flush_bg_loading_exception(self):
        __traceback_hide__ = True  # noqa: F841
        exc_info = self._bg_loading_exc_info
        if exc_info is not None:
            self._bg_loading_exc_info = None
            raise exc_info

    def _load_unlocked(self):
        __traceback_hide__ = True  # noqa: F841
        self._app = rv = self.loader()
        self._bg_loading_exc_info = None
        return rv

    def __call__(self, environ, start_response):
        __traceback_hide__ = True  # noqa: F841
        if self._app is not None:
            return self._app(environ, start_response)
        self._flush_bg_loading_exception()
        with self._lock:
            if self._app is not None:
                rv = self._app
            else:
                rv = self._load_unlocked()
            return rv(environ, start_response)


class ScriptInfo:
    """Helper object to deal with PyOSLC applications.  This is usually not
    necessary to interface with as it's used internally in the dispatching
    to click.  In future versions of PyOSLC this object will most likely play
    a bigger role.  Typically it's created automatically by the
    :class:`OSLCGroup` but you can also manually create it and pass it
    onwards as click object.
    """

    def __init__(self, app_import_path=None, create_app=None, set_debug_flag=True):
        #: Optionally the import path for the PyOSLC application.
        self.app_import_path = app_import_path or os.environ.get("PYOSLC_APP")
        #: Optionally a function that is passed the script info to create
        #: the instance of the application.
        self.create_app = create_app
        #: A dictionary with arbitrary data that can be associated with
        #: this script info.
        self.data = {}
        self.set_debug_flag = set_debug_flag
        self._loaded_app = None

    def load_app(self):
        """Loads the PyOSLC app (if not yet loaded) and returns it.  Calling
        this multiple times will just result in the already loaded app to
        be returned.
        """
        __traceback_hide__ = True  # noqa: F841

        if self._loaded_app is not None:
            return self._loaded_app

        if self.create_app is not None:
            app = call_factory(self, self.create_app)
        else:
            if self.app_import_path:
                path, name = (
                    re.split(r":(?![\\/])", self.app_import_path, 1) + [None]
                )[:2]
                import_name = prepare_import(path)
                app = locate_app(self, import_name, name)
            else:
                for path in ("wsgi.py", "app.py"):
                    import_name = prepare_import(path)
                    app = locate_app(self, import_name, None, raise_if_not_found=False)

                    if app:
                        break

        if not app:
            raise NoAppException(
                "Could not locate a PyOSLC application. You did not provide "
                'the "PYOSLC_APP" environment variable, and a "wsgi.py" or '
                '"app.py" module was not found in the current directory.'
            )

        if self.set_debug_flag:
            # Update the app's debug flag through the descriptor so that
            # other values repopulate as well.
            app.debug = get_debug_flag()

        self._loaded_app = app
        return app


pass_script_info = click.make_pass_decorator(ScriptInfo, ensure=True)


def with_appcontext(f):
    """Wraps a callback so that it's guaranteed to be executed with the
    script's application context.  If callbacks are registered directly
    to the ``app.cli`` object then they are wrapped with this function
    by default unless it's disabled.
    """

    @click.pass_context
    def decorator(__ctx, *args, **kwargs):
        with __ctx.ensure_object(ScriptInfo).load_app().app_context():
            return __ctx.invoke(f, *args, **kwargs)

    return update_wrapper(decorator, f)


def get_env() -> str:
    """Get the environment the app is running in, indicated by the
    :envvar:`PYOSLC_ENV` environment variable. The default is
    ``'production'``.
    """
    return os.environ.get("PYOSLC_ENV") or "production"


def get_debug_flag() -> bool:
    """Get whether debug mode should be enabled for the app, indicated
    by the :envvar:`PYOSLC_DEBUG` environment variable. The default is
    ``True`` if :func:`.get_env` returns ``'development'``, or ``False``
    otherwise.
    """
    val = os.environ.get("PYOSLC_DEBUG")

    if not val:
        return get_env() == "development"

    return val.lower() not in ("0", "false", "no")


class AppGroup(click.Group):
    """This works similar to a regular click :class:`~click.Group` but it
    changes the behavior of the :meth:`command` decorator so that it
    automatically wraps the functions in :func:`with_appcontext`.

    Not to be confused with :class:`OSLCGroup`.
    """

    # def command(self, *args, **kwargs):
    #     """This works exactly like the method of the same name on a regular
    #     :class:`click.Group` but it wraps callbacks in :func:`with_appcontext`
    #     unless it's disabled by passing ``with_appcontext=False``.
    #     """
    #     wrap_for_ctx = kwargs.pop("with_appcontext", True)
    #
    #     def decorator(f):
    #         if wrap_for_ctx:
    #             f = with_appcontext(f)
    #         return click.Group.command(self, *args, **kwargs)(f)
    #
    #     return decorator

    # def group(self, *args, **kwargs):
    #     """This works exactly like the method of the same name on a regular
    #     :class:`click.Group` but it defaults the group class to
    #     :class:`AppGroup`.
    #     """
    #     kwargs.setdefault("cls", AppGroup)
    #     return click.Group.group(self, *args, **kwargs)


class OSLCGroup(AppGroup):
    """Special subclass of the :class:`AppGroup` group that supports
    loading more commands from the configured PyOSLC app.  Normally a
    developer does not have to interface with this class but there are
    some very advanced use cases for which it makes sense to create an
    instance of this. see :ref:`custom-scripts`.

    :param add_default_commands: if this is True then the default run and
        shell commands will be added.
    :param add_version_option: adds the ``--version`` option.
    :param create_app: an optional callback that is passed the script info and
        returns the loaded app.
    :param load_dotenv: Load the nearest :file:`.env` and :file:`.pyoslcenv`
        files to set environment variables. Will also change the working
        directory to the directory containing the first file found.
    :param set_debug_flag: Set the app's debug flag based on the active
        environment

    .. versionchanged:: 1.0
        If installed, python-dotenv will be used to load environment variables
        from :file:`.env` and :file:`.pyoslcenv` files.
    """

    def __init__(
        self,
        add_default_commands=True,
        create_app=None,
        add_version_option=True,
        load_dotenv=True,
        set_debug_flag=True,
        **extra,
    ):
        params = list(extra.pop("params", None) or ())

        if add_version_option:
            params.append(version_option)

        AppGroup.__init__(self, params=params, **extra)
        self.create_app = create_app
        self.load_dotenv = load_dotenv
        self.set_debug_flag = set_debug_flag

        if add_default_commands:
            self.add_command(run_command)

        self._loaded_plugin_commands = False

    def get_command(self, ctx, name):
        # self._load_plugin_commands()
        # Look up built-in and plugin commands, which should be
        # available even if the app fails to load.
        rv = super().get_command(ctx, name)

        if rv is not None:
            return rv

        info = ctx.ensure_object(ScriptInfo)

        # Look up commands provided by the app, showing an error and
        # continuing if the app couldn't be loaded.
        try:
            return info.load_app().cli.get_command(ctx, name)
        except NoAppException as e:
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")

    def list_commands(self, ctx):
        # Start with the built-in and plugin commands.
        rv = set(super().list_commands(ctx))
        info = ctx.ensure_object(ScriptInfo)

        # Add commands provided by the app, showing an error and
        # continuing if the app couldn't be loaded.
        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except NoAppException as e:
            # When an app couldn't be loaded, show the error message
            # without the traceback.
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
        except Exception:
            # When any other errors occurred during loading, show the
            # full traceback.
            click.secho(f"{traceback.format_exc()}\n", err=True, fg="red")

        return sorted(rv)

    def main(self, *args, **kwargs):
        # Set a global flag that indicates that we were invoked from the
        # command line interface. This is detected by PyOSLC.run to make the
        # call into a no-op. This is necessary to avoid ugly errors when the
        # script that is loaded here also attempts to start a server.
        os.environ["PYOSLC_RUN_FROM_CLI"] = "true"

        load_dotenv()

        obj = kwargs.get("obj")

        if obj is None:
            obj = ScriptInfo(
                create_app=self.create_app, set_debug_flag=self.set_debug_flag
            )

        kwargs["obj"] = obj
        kwargs.setdefault("auto_envvar_prefix", "PYOSLC")
        return super().main(*args, **kwargs)


def load_dotenv(path=None):
    """Load "dotenv" files in order of precedence to set environment variables.

    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files.

    This is a no-op if `python-dotenv`_ is not installed.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: Load the file at this location instead of searching.
    :return: ``True`` if a file was loaded.

    .. versionchanged:: 1.1.0
        Returns ``False`` when python-dotenv is not installed, or when
        the given path isn't a file.

    .. versionchanged:: 2.0
        When loading the env files, set the default encoding to UTF-8.

    .. versionadded:: 1.0
    """
    if dotenv is None:
        if path or os.path.isfile(".env") or os.path.isfile(".pyoslcenv"):
            click.secho(
                " * Tip: There are .env or .pyoslcenv files present."
                ' Do "pip install python-dotenv" to use them.',
                fg="yellow",
                err=True,
            )

        return False

    # if the given path specifies the actual file then return True,
    # else False
    if path is not None:
        if os.path.isfile(path):
            return dotenv.load_dotenv(path, encoding="utf-8")

        return False

    new_dir = None

    for name in (".env", ".pyoslcenv"):
        path = dotenv.find_dotenv(name, usecwd=True)

        if not path:
            continue

        if new_dir is None:
            new_dir = os.path.dirname(path)

        dotenv.load_dotenv(path, encoding="utf-8")

    return new_dir is not None  # at least one file was located and loaded


def show_server_banner(env, debug, app_import_path, eager_loading):
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return

    if app_import_path is not None:
        message = f" * Serving PyOSLC app {app_import_path!r}"

        if not eager_loading:
            message += " (lazy loading)"

        click.echo(message)

    click.echo(f" * Environment: {env}")

    if env == "production":
        click.secho(
            "   WARNING: This is a development server. Do not use it in"
            " a production deployment.",
            fg="red",
        )
        click.secho("   Use a production WSGI server instead.", dim=True)

    if debug is not None:
        click.echo(f" * Debug mode: {'on' if debug else 'off'}")


@click.command("run", short_help="Run a development server.")
@click.option("--host", "-h", default="127.0.0.1", help="The interface to bind to.")
@click.option("--port", "-p", default=5000, help="The port to bind to.")
@click.option(
    "--reload/--no-reload",
    default=None,
    help="Enable or disable the reloader. By default the reloader "
    "is active if debug is enabled.",
)
@click.option(
    "--debugger/--no-debugger",
    default=None,
    help="Enable or disable the debugger. By default the debugger "
    "is active if debug is enabled.",
)
@click.option(
    "--eager-loading/--lazy-loading",
    default=None,
    help="Enable or disable eager loading. By default eager "
    "loading is enabled if the reloader is disabled.",
)
@click.option(
    "--with-threads/--without-threads",
    default=True,
    help="Enable or disable multithreading.",
)
@pass_script_info
def run_command(
    info, host, port, reload, debugger, eager_loading, with_threads
):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    PYOSLC_ENV=development or PYOSLC_DEBUG=1.
    """
    debug = get_debug_flag()

    if reload is None:
        reload = debug

    if debugger is None:
        debugger = debug

    show_server_banner(get_env(), debug, info.app_import_path, eager_loading)
    app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    from werkzeug.serving import run_simple

    run_simple(
        host,
        port,
        app,
        use_reloader=reload,
        use_debugger=debugger,
        threaded=with_threads,
        # ssl_context=cert,
        # extra_files=extra_files,
    )


cli = OSLCGroup(
    help="""\
A command line script to run a PyOSLC application.

Loads the application defined in the PYOSLC_APP environment variable, or from a wsgi.py
file. Setting the PYOSLC_ENV environment variable to 'development' will enable
debug mode.

\b
  {prefix}{cmd} PYOSLC_APP=hello.py
  {prefix}{cmd} PYOSLC_ENV=development
  {prefix}pyoslc run
""".format(
        cmd="export" if os.name == "posix" else "set",
        prefix="$ " if os.name == "posix" else "> ",
    )
)


def main() -> None:
    if int(click.__version__[0]) < 8:
        warnings.warn(
            "Using the `pyoslc` cli with Click 7 is deprecated and"
            " will not be supported starting with PyOSLC 2.1."
            " Please upgrade to Click 8 as soon as possible.",
            DeprecationWarning,
        )
    # TODO omit sys.argv once https://github.com/pallets/click/issues/536 is fixed
    cli.main(args=sys.argv[1:])


if __name__ == "__main__":
    main()
