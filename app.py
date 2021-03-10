import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import boto3
import io
import os

# import time
# from concurrent.futures import ThreadPoolExecutor

# Suppress chained assignment warning
pd.options.mode.chained_assignment = None  # default='warn'

# Load s3 environment variables
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


# Functions
def make_graph(df):
    """Take in a dataframe and make a pretty interactive graph.

    Args:
        df (pd.DataFrame): dataframe of covid data

    Returns:
        fig: plotly figure object
        week_to_week: str explaining % change over time in new cases
    """

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.iloc[1:]
    df["RollingCase"] = df["Case"].rolling(3).mean()
    df["RollingNew"] = df["New"].rolling(3).mean()
    df["Real"] = df["Case"].diff()
    df["RollingReal"] = df["Real"].rolling(3).mean()

    def weird_division(n, d):
        return n / d if d else 0

    def find_weekly_change(df):
        new_df = df.set_index("Date").resample("1D").first()
        week_to_week = int(
            100
            * (
                weird_division(
                    new_df["Real"].iloc[-7:].mean(), new_df["Real"].iloc[-14:-7].mean()
                )
                - 1
            )
        )
        return weekly_text(week_to_week)

    def weekly_text(week_to_week):
        if week_to_week > 0:
            return f"On average, new cases are up {week_to_week}% week over week."
        return f"On average, new cases are down {week_to_week}% week over week."

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Real"],
            mode="markers",
            name="New Cases",
            marker={"color": "lightskyblue"},
            yaxis="y2",
            showlegend=False,
            # width=1000 * 3600 * 24 * 0.5,
            # offset=1000 * 3600 * 24 * 0.5,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Case"],
            mode="markers",
            name="Total Cases",
            marker={"color": "lightpink"},
            showlegend=False,
            # width=1000 * 3600 * 24 * 0.5,
            # yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RollingCase"],
            mode="lines",
            name="Average Total Cases",
            line={"color": "tomato"},
            # showlegend=False,
            # yaxis="y2",
            fill="tozeroy",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RollingReal"],
            mode="lines",
            name="Average New Cases",
            line={"color": "blue"},
            # showlegend=False,
            yaxis="y2",
            fill="tozeroy",
        )
    )

    fig.update_layout(
        yaxis2=dict(
            title="New Cases",
            titlefont=dict(color="blue"),
            anchor="x",
            overlaying="y",
            side="right",
            range=[0, 15],
            # tickfont=dict(color="#1f77b4"),
        ),
        yaxis=dict(
            title="Total Cases",
            titlefont=dict(color="lightcoral"),
            # tickfont=dict(color="#d62728"),
        ),
        xaxis_title="Date",
        template="ggplot2",
        legend=dict(orientation="v", yanchor="bottom", y=0.8, xanchor="left", x=0),
        margin={"t": 40, "r": 40, "l": 40, "b": 40},
    )

    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")

    fig.update_xaxes(tickformat="%b %d")

    return fig, find_weekly_change(df)


def get_s3_data():
    """Retrieve latest covid data from Amazon s3 bucket and process to a dataframe.

    Returns:
        pd.DataFrame: Dataframe of covid data
    """
    s3_client = boto3.client("s3")
    BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    OBJECT_NAME = "msu_covid.csv"
    bytes_buffer = io.BytesIO()

    s3_client.download_fileobj(
        Bucket=BUCKET_NAME, Key=OBJECT_NAME, Fileobj=bytes_buffer
    )
    byte_value = bytes_buffer.getvalue()
    str_value = byte_value.decode()

    df = pd.read_csv(io.StringIO(str_value), header=0)
    return df


# RELOAD_INTERVAL = 24 * 3600  # reload interval in seconds, 24 hours


# def refresh_data_every():
#     """Threa executor loop to refresh data every 24 hours."""
#     while True:
#         refresh_data()
#         time.sleep(RELOAD_INTERVAL)


# def refresh_data():
#     """Grab fresh data from Amazon S3 and set to a global data variable."""
#     global data
#     data = get_s3_data()


def make_layout():
    """Layout must be a function so that each page load recreates layout.

    See: https://community.plotly.com/t/solved-updating-server-side-app-data-on-a-schedule/6612."""  # noqa
    data = get_s3_data()
    fig, week_to_week_text = make_graph(data)
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H4(
                                    "MSU Denver COVID Cases", className="card-title"
                                ),
                            ),
                            dbc.CardBody(
                                [
                                    dcc.Graph(
                                        figure=fig, config={"displayModeBar": False}
                                    )
                                ]
                            ),
                            dbc.CardFooter(
                                [
                                    html.P(week_to_week_text, className="float-left"),
                                    html.P(
                                        [
                                            "Designed by ",
                                            html.A(
                                                "Dr. Andrew J. Bonham",
                                                href="https://github.com/Paradoxdruid",
                                            ),
                                        ],
                                        className="float-right",
                                    ),
                                ],
                            ),
                        ],
                        className="shadow-lg border-primary mb-3",
                        style={"min-width": "550px"},
                    ),
                    width={"size": 6, "offset": 3},
                    style={"min-width": "600px"},
                ),
                style={"padding-top": "40px"},
            ),
        ],
        fluid=True,
        className="bg-secondary",
        style={"min-height": "100vh"},
    )


# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "google", "content": "notranslate"}],
)
server = app.server
app.title = "MSU COVID"

# # Get initial data
# refresh_data()

# Provide layout at function for refresh on page load
app.layout = make_layout

# # Run the data refresh function in another thread
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(refresh_data_every)

if __name__ == "__main__":
    app.run_server(debug=True)
