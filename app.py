import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
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
    week_to_week = int(
        100 * ((df["New"].iloc[-7:].mean() / df["New"].iloc[-14:-7].mean()) - 1)
    )

    def weekly_text(week_to_week):
        if week_to_week > 0:
            return f"On average, new cases are up {week_to_week}% week over week."
        else:
            return f"On average, new cases are down {week_to_week}% week over week."

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Case"],
            mode="markers",
            name="Total Cases",
            marker={"color": "red"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["New"],
            mode="markers",
            name="New Cases",
            marker={"color": "blue"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RollingCase"],
            mode="lines",
            name="Average Total Cases",
            line={"color": "red"},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RollingNew"],
            mode="lines",
            name="Average New Cases",
            line={"color": "blue"},
            showlegend=False,
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cases",
        template="ggplot2",
        legend=dict(orientation="v", yanchor="bottom", y=0.4, xanchor="right", x=1),
        margin={"t": 40, "r": 40, "l": 40, "b": 40},
    )

    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")

    fig.update_xaxes(dtick="D1", tickformat="%b %d")

    return fig, weekly_text(week_to_week)


fig, week_to_week = make_graph("msu_covid.csv")
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H4("MSU Denver COVID Cases", className="card-title"),
                        ),
                        dbc.CardBody([dcc.Graph(figure=fig)]),
                        dbc.CardFooter(html.P(week_to_week)),
                    ],
                    className="shadow-lg border-primary mb-3",
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
    app.run_server()
