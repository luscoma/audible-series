"""
A commandlet for the audible cli that outputs series with unpurchased books.

To use first generate a library file via audible_cli library export then run
this command.  A config file can be used to skip unwanted series or already
preordered books -- see configfile.py for options.
"""
import audible
import click
from audible_cli.decorators import pass_session

from audible_series import seriesutil
from audible_series import configfile


@click.command("series")
@click.option(
    "--library", "-l",
    multiple=False,
    required=True,
    help="The exported library to check, generate via `library export` cmd."
)
@click.option(
    "--config",
    "-c",
    multiple=False,
    required=False,
    help="YAML config with series to skip and book overrides"
)
@click.option(
    "--only_series",
    "-o",
    multiple=True,
    required=False,
    help="Limit to just these series"
)
@pass_session
def cli(session, library, config, only_series):
    "Print out any series where there is a new book unpurchased"
    options = configfile.load(config)
    all_series = seriesutil.parse_library(
        library,
        options.series_to_skip
    )
    latest_in_series = seriesutil.extract_latest_in_series(
        all_series,
        options.external_library
    )

    display_warnings(latest_in_series, options)

    # Useful when debugging
    if only_series:
        latest_in_series = {
            k: v for k, v in latest_in_series.items() if k in only_series}

    librarian = seriesutil.Librarian.create()
    click.echo("Fetching series data, this may take a moment...")
    with audible.Client(auth=session.auth) as client, click.progressbar(
            latest_in_series.items()) as series_books:
        for series_title, book in series_books:
            response = client.get(f"catalog/products/{book.asin}/sims",
                                  response_groups="product_desc,product_attrs",
                                  similarity_type="NextInSameSeries")
            book = seriesutil.parse_sims_response(response, series_title)
            librarian.classify(series_title, book, options)

    click.echo_via_pager(librarian.format_for_click())


def display_warnings(latest_in_series, options):
    """Displays warnings."""
    # To save typos, we alert for any unused external library series
    for series_title in options.external_library.keys():
        if series_title not in latest_in_series:
            click.secho(
                f"Warning: Override not applied for {series_title}, not in library",
                fg='red'
            )

    # Verify no preorders have are now actually in the library
    for book in latest_in_series.values():
        if book.asin in options.preordered_asins:
            click.secho(
                f"Warning: Preorder {book.title} in {book.series_title} ({book.asin}) is library "
                "already",
                fg="bright_red")
