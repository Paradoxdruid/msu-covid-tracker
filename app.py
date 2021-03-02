import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "google", "content": "notranslate"}],
)
server = app.server

app.title = "MSU COVID"


# Functions
def make_graph(csv_filename):
    """Take in a dataframe and make a pretty interactive graph.

    Args:
        csv_filename (str): csv_filename

    Returns:
        fig: plotly figure object
        week_to_week: str explaining % change over time in new cases
    """

    df = pd.read_csv(csv_filename, header=0)
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
        go.Bar(
            x=df["Date"],
            y=df["Real"],
            # mode="markers",
            name="New Cases",
            marker={"color": "lightskyblue"},
            yaxis="y2",
            width=1000 * 3600 * 24 * 0.5,
            offset=1000 * 3600 * 24 * 0.5,
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Case"],
            # mode="markers",
            name="Total Cases",
            marker={"color": "lightpink"},
            width=1000 * 3600 * 24 * 0.5,
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
            showlegend=False,
            # yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RollingReal"],
            mode="lines",
            name="Average New Cases",
            line={"color": "blue"},
            showlegend=False,
            yaxis="y2",
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


fig, week_to_week_text = make_graph("msu_covid.csv")
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H4("MSU Denver COVID Cases", className="card-title"),
                        ),
                        dbc.CardBody(
                            [dcc.Graph(figure=fig, config={"displayModeBar": False})]
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

if __name__ == "__main__":
    app.run_server(debug=True)
